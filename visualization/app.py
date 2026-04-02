import streamlit as st
import pydeck as pdk
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import os
import json

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Mapbox basemaps (PyDeck) read MAPBOX_API_KEY in hosted environments
_mapbox = os.getenv("MAPBOX_API_KEY")
if _mapbox:
    os.environ["MAPBOX_API_KEY"] = _mapbox

st.set_page_config(
    page_title="Colorado Fire Watch",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container h1 {
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 0.15rem;
        }
        p.cfw-lead {
            color: #9aa0a6;
            font-size: 1.05rem;
            margin-top: 0;
            margin-bottom: 1.25rem;
        }
        div[data-testid="stMetricValue"] {
            font-variant-numeric: tabular-nums;
        }
        .cfw-footer {
            font-size: 0.82rem;
            color: #8b949e;
            margin-top: 2rem;
            padding-top: 1.1rem;
            border-top: 1px solid #30363d;
            line-height: 1.5;
        }
        .cfw-footer a { color: #e0702e; text-decoration: none; }
        .cfw-footer a:hover { text-decoration: underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Colorado Fire Watch")
st.markdown(
    '<p class="cfw-lead">Near-real-time NASA VIIRS fire detections in Colorado, '
    "clustered in PostGIS, with optional MTBS historical burn perimeters for context.</p>",
    unsafe_allow_html=True,
)

_db_url = os.getenv("DATABASE_URL")
if not _db_url:
    st.error("Set **DATABASE_URL** in `.env` at the project root (or in deployment secrets).")
    st.stop()

engine = create_engine(_db_url, pool_pre_ping=True)

def get_clusters():
    with engine.connect() as conn:
        result = conn.execute(text("""
            WITH clustered AS (
                SELECT 
                    detection_id,
                    detection_date,
                    latitude,
                    longitude,
                    brightness,
                    confidence,
                    ST_ClusterDBSCAN(ST_Transform(geom, 26913), eps := 5000, minpoints := 2) OVER () as cluster_id
                FROM raw_fire_detections
                WHERE detection_date >= CURRENT_DATE - INTERVAL '14 days'
            )
            SELECT 
                cluster_id,
                COUNT(detection_id) AS detection_count,
                AVG(longitude) AS centroid_lon,
                AVG(latitude) AS centroid_lat,
                MAX(brightness) AS max_brightness,
                bool_or(confidence = 'h') AS has_high_confidence,
                MIN(detection_date) AS first_detected,
                MAX(detection_date) AS last_detected
            FROM clustered
            WHERE cluster_id IS NOT NULL
            GROUP BY cluster_id
            ORDER BY max_brightness DESC
        """))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

def get_daily_trend():
    with engine.connect() as conn:
        result = conn.execute(text("""
            WITH daily_counts AS (
                SELECT
                    detection_date,
                    COUNT(*) AS detection_count
                FROM raw_fire_detections
                GROUP BY detection_date
            )
            SELECT
                detection_date,
                detection_count,
                AVG(detection_count) OVER (
                    ORDER BY detection_date
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ) AS rolling_3_day_avg
            FROM daily_counts
            ORDER BY detection_date
        """))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

def get_perimeters():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                fire_name,
                fire_year,
                acres,
                ST_AsGeoJSON(geom) AS geometry
            FROM fire_perimeters
            WHERE geom IS NOT NULL
        """))
        return pd.DataFrame(result.fetchall(), columns=result.keys())


def perimeters_to_geojson(df: pd.DataFrame) -> dict:
    """GeoJsonLayer expects a GeoJSON object, not a DataFrame."""
    features = []
    for _, row in df.iterrows():
        geom_raw = row.get("geometry")
        if geom_raw is None or (isinstance(geom_raw, float) and pd.isna(geom_raw)):
            continue
        if isinstance(geom_raw, str):
            geom = json.loads(geom_raw)
        else:
            geom = geom_raw
        if not geom:
            continue
        fy = int(row["fire_year"]) if pd.notna(row.get("fire_year")) else None
        ac = float(row["acres"]) if pd.notna(row.get("acres")) else None
        fn = str(row["fire_name"]) if pd.notna(row.get("fire_name")) else ""
        props = {
            "detection_count": "—",
            "max_brightness": "—",
            "last_detected": "—",
            "fire_name": fn,
            "fire_year": fy if fy is not None else "—",
            "acres": ac if ac is not None else "—",
            "layer_note": "Historical MTBS burn boundary — not active fire",
        }
        feat = {
            "type": "Feature",
            "properties": props,
            "geometry": geom,
        }
        # Deck tooltip substitution often reads the picked object root; mirror props there too
        feat.update(props)
        features.append(feat)
    return {"type": "FeatureCollection", "features": features}

def dataframe_to_pydeck_records(df: pd.DataFrame, cols: list[str]) -> list[dict]:
    """PyDeck serializes to JSON with vars(); numpy/Decimal from pandas/SQL break that path."""
    if df.empty:
        return []
    int_cols = {"detection_count", "cluster_id"}
    float_cols = {"centroid_lon", "centroid_lat", "max_brightness"}
    out = []
    for _, row in df[cols].iterrows():
        rec = {}
        for c in cols:
            v = row[c]
            if hasattr(v, "item"):
                v = v.item()
            if pd.isna(v):
                rec[c] = None
            elif c in int_cols:
                rec[c] = int(v)
            elif c in float_cols:
                rec[c] = float(v)
            else:
                rec[c] = str(v)
        mb = rec["max_brightness"]
        tip = {
            "detection_count": rec["detection_count"],
            "max_brightness": f"{mb:.1f} K",
            "last_detected": rec["last_detected"],
            "fire_name": "—",
            "fire_year": "—",
            "acres": "—",
            "layer_note": "VIIRS detection cluster (last 14 days)",
        }
        rec["properties"] = tip
        rec.update(tip)
        out.append(rec)
    return out


def _last_detected_label(df: pd.DataFrame) -> str:
    if df.empty:
        return "—"
    m = df["last_detected"].max()
    if pd.isna(m):
        return "—"
    return str(m)


def _db_err_text(exc: BaseException) -> str:
    if isinstance(exc, OperationalError) and getattr(exc, "orig", None):
        return str(exc.orig)
    return str(exc)


try:
    df_clusters = get_clusters()
    df_clusters["max_brightness"] = df_clusters["max_brightness"].astype(float).round(1)
    df_clusters["detection_count"] = df_clusters["detection_count"].astype(int)
    df_clusters["last_detected"] = df_clusters["last_detected"].astype(str)
    df_trend = get_daily_trend()
    df_perimeters = get_perimeters()
except OperationalError as e:
    msg = _db_err_text(e)
    if (
        "could not translate host name" in msg
        or "getaddrinfo" in msg.lower()
        or "Name or service not known" in msg
    ):
        st.error("Could not resolve the database host (common on Windows with Supabase).")
        st.markdown(
            r"""
**This is not a Docker issue.** Your app reads **`DATABASE_URL`** from `.env` only.

The direct host **`db.<project>.supabase.co`** often has **IPv6-only** DNS. Many Windows/Python stacks
then fail DNS (`getaddrinfo` / could not translate host name).

**Fix — use one of these:**

1. **Session pooler URI (recommended)**  
   Supabase → **Project Settings** → **Database** → **Connection string** → choose **Session pooler**
   (or **Transaction** if you use port 6543). Copy the URI — host looks like **`…pooler.supabase.com`**
   and usually works over **IPv4**.  
   Set that full string as **`DATABASE_URL`** (keep `?sslmode=require` or add `&sslmode=require`).  
   Pooler usernames often look like **`postgres.<project-ref>`** — use exactly what the dashboard shows.

2. **IPv4 add-on**  
   Supabase → **Project Settings** → **Add-ons** → **IPv4** for the project, then the direct `db.*` host
   can work from IPv4-only networks.

3. **Quick check:** `nslookup -type=A your-hostname` — if there is **no A record**, use (1) or (2).
"""
        )
        st.stop()
    raise

perimeter_geojson = perimeters_to_geojson(df_perimeters)

map_cols = [
    "centroid_lon",
    "centroid_lat",
    "detection_count",
    "max_brightness",
    "last_detected",
]
map_data = dataframe_to_pydeck_records(df_clusters, map_cols)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position=["centroid_lon", "centroid_lat"],
    get_radius="detection_count * 1000",
    get_fill_color=[255, 100, 0, 160],
    pickable=True,
    auto_highlight=True
)

perimeter_layer = pdk.Layer(
    "GeoJsonLayer",
    id="mtbs-historical-perimeters",
    data=perimeter_geojson,
    filled=True,
    stroked=True,
    # Cool blue-gray = historical context; orange scatter = active-ish detections
    get_fill_color=[90, 130, 180, 55],
    get_line_color=[160, 190, 220, 240],
    line_width_min_pixels=1.5,
    pickable=True,
)

view = pdk.ViewState(
    latitude=38.5,
    longitude=-105.5,
    zoom=6,
    pitch=0
)

if df_clusters.empty and df_perimeters.empty:
    st.info(
        "Database is connected, but **there is no data to display yet**. "
        "Point **`DATABASE_URL`** at this Supabase project and run **`python -m ingestion.firms_ingest`** "
        "(with **`FIRMS_API_KEY`** set) to fill `raw_fire_detections`. "
        "Optional: run **`python -m ingestion.mtbs_ingest`** after configuring the MTBS shapefile path for `fire_perimeters`."
    )
elif df_clusters.empty:
    st.warning(
        "No detection **clusters** in the last **14 days** — either ingest new FIRMS data, "
        "or your `raw_fire_detections` rows are older than the rolling window."
    )
elif df_perimeters.empty:
    st.info(
        "**Historical perimeters:** the `fire_perimeters` table has no rows in this database yet. "
        "FIRMS and MTBS are separate loads. Download the MTBS perimeter shapefile, set **`MTBS_SHAPEFILE_PATH`** "
        "in `.env`, keep **`DATABASE_URL`** pointed at Supabase, then run: "
        "`python -m ingestion.mtbs_ingest`"
    )

with st.sidebar:
    st.header("Situation Report")
    st.caption(f"Last updated: {_last_detected_label(df_clusters)}")

    st.metric("Active Clusters", len(df_clusters))
    st.metric("Total Detections", int(df_clusters["detection_count"].sum()))
    st.metric("MTBS perimeters loaded", len(df_perimeters))

    st.divider()
    st.subheader("Map layers")
    show_historical = st.checkbox(
        "Historical burn perimeters (MTBS)",
        value=True,
        help=(
            "MTBS shows mapped **past** fire footprints (final perimeter), "
            "not live or active fire outlines. Use for context only."
        ),
    )

    st.divider()

    for _, row in df_clusters.iterrows():
        with st.expander(f"Cluster {int(row['cluster_id'])} — {row['last_detected']}"):
            st.write(f"Detections: {int(row['detection_count'])}")
            st.write(f"Max brightness: {row['max_brightness']:.1f}K")
            st.write(f"High confidence: {'Yes' if row['has_high_confidence'] else 'No'}")
            st.write(f"Location: {row['centroid_lat']:.3f}, {row['centroid_lon']:.3f}")

    st.divider()
    with st.expander("About"):
        st.markdown(
            "**Stack:** Streamlit, PyDeck, PostGIS (Supabase), SQLAlchemy. "
            "Detections from NASA FIRMS; historical shapes from MTBS where loaded.\n\n"
            "**Note:** For research and situational awareness only. "
            "Not an official fire-management or life-safety system.\n\n"
            "[Source on GitHub](https://github.com/kemurphy3/colorado-fire-watch)"
        )

map_layers = [layer]
if show_historical:
    map_layers.insert(0, perimeter_layer)

st.markdown(
    "**Map legend:** Orange points are VIIRS detection clusters (last 14 days). "
    "Blue-gray polygons are **historical** MTBS burn boundaries (past mapped perimeters only). "
    "Toggle MTBS in the sidebar."
)

st.pydeck_chart(
    pdk.Deck(
        layers=map_layers,
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={
            "html": (
                "<small>{layer_note}</small><br/><br/>"
                "<b>Active detection cluster</b><br/>"
                "<b>Detections:</b> {detection_count}<br/>"
                "<b>Max brightness:</b> {max_brightness}<br/>"
                "<b>Last seen:</b> {last_detected}<br/><br/>"
                "<b>Historical perimeter (MTBS)</b><br/>"
                "<b>Fire:</b> {fire_name}<br/>"
                "<b>Year:</b> {fire_year} &nbsp; <b>Acres:</b> {acres}"
            ),
            "style": {"backgroundColor": "#1e2a36", "color": "#e8eaed"},
        },
    ),
    use_container_width=True,
)

st.subheader("Detection Trend")
trend_chart_df = df_trend.copy()
trend_chart_df["detection_date"] = pd.to_datetime(trend_chart_df["detection_date"])
trend_chart_df["detection_count"] = pd.to_numeric(trend_chart_df["detection_count"], errors="coerce")
trend_chart_df["rolling_3_day_avg"] = pd.to_numeric(trend_chart_df["rolling_3_day_avg"], errors="coerce")
trend_chart_df = trend_chart_df.set_index("detection_date")[["detection_count", "rolling_3_day_avg"]]

if trend_chart_df.dropna(how="all").empty:
    st.info("No trend data available yet. Add more detections to see the chart.")
else:
    st.line_chart(trend_chart_df)

st.markdown(
    """
    <div class="cfw-footer">
    <strong>Data sources:</strong> NASA FIRMS VIIRS near-real-time detections; USGS MTBS historical burn perimeters where ingested.
    Citations: NASA FIRMS; MTBS program.
    This tool is not operationally certified for emergency response.
    <a href="https://github.com/kemurphy3/colorado-fire-watch" target="_blank" rel="noopener noreferrer">Repository</a>
    </div>
    """,
    unsafe_allow_html=True,
)
