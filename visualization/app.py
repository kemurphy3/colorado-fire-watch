import streamlit as st
import pydeck as pdk
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import json

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

st.set_page_config(
    page_title="Colorado Fire Watch",
    layout="wide"
)

st.title("Colorado Fire Watch")
st.caption("Near-real-time NASA satellite fire detection in Colorado")

engine = create_engine(os.getenv("DATABASE_URL"))

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


df_clusters = get_clusters()
df_clusters['max_brightness'] = df_clusters['max_brightness'].astype(float).round(1)
df_clusters['detection_count'] = df_clusters['detection_count'].astype(int)
df_clusters['last_detected'] = df_clusters['last_detected'].astype(str)
df_trend = get_daily_trend()
df_perimeters = get_perimeters()
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

with st.sidebar:
    st.header("Situation Report")
    st.caption(f"Last updated: {df_clusters['last_detected'].max()}")

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

map_layers = [layer]
if show_historical:
    map_layers.insert(0, perimeter_layer)

st.caption(
    "**Legend:** Orange dots = FIRMS detection clusters (rolling 14 days). "
    "Blue-gray polygons = **historical** MTBS burn boundaries (past fires only; not active perimeters). "
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
            "style": {"backgroundColor": "#2e4057", "color": "white"},
        },
    )
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