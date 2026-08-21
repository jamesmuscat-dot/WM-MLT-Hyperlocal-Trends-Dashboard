import base64
import html
import math
import re
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

st.set_page_config(
    page_title="Hyperlocal & Trend Range Analytics",
    layout="wide",
)

st.markdown(
    """
    <style>
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1600px;
        }
        .stApp {
            background: #f7f8fc;
        }
        div[data-testid="stTabs"] {
            margin-top: 0 !important;
            position: relative;
            z-index: 10;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

MAP_HEIGHT = 520
CHART_HEIGHT = 320
TOP_ROW_GAP = 14
SECTION_GAP = 12
CATEGORY_TILE_DIR = Path("assets/category_titles")
PROFILE_PIC_DIR = Path("assets/profile_pics")
TREND_IMAGE_DIR = Path("assets/trend_images")
PLATFORM_ICON_DIR = Path("assets/platform_icon")

PLATFORM_ICON_FILES = {
    "Instagram": PLATFORM_ICON_DIR / "ins.jpg",
    "TikTok": PLATFORM_ICON_DIR / "tiktok.jpg",
}

ASSISTANT_ICON_FILES = {
    "Claude": PLATFORM_ICON_DIR / "claude.jpg",
    "ChatGPT": PLATFORM_ICON_DIR / "gpt.jpg",
}

CATEGORY_TILES = {
    "Bakeries": str(CATEGORY_TILE_DIR / "bakeries.jpg"),
    "Coffee Roasteries": str(CATEGORY_TILE_DIR / "coffee_roasteries.jpg"),
    "Breweries": str(CATEGORY_TILE_DIR / "breweries.jpg"),
    "Distilleries": str(CATEGORY_TILE_DIR / "distilleries.jpg"),
    "Delicatessen": str(CATEGORY_TILE_DIR / "delicatessen.jpg"),
    "Butcher Shops": str(CATEGORY_TILE_DIR / "butcher_shops.jpg"),
    "Seafood Producers": str(CATEGORY_TILE_DIR / "seafood_producers.jpg"),
    "Local Soft Drinks": str(CATEGORY_TILE_DIR / "local_soft_drinks.jpg"),
    "Local Snacks": str(CATEGORY_TILE_DIR / "local_snacks.jpg"),
    "Fruits & Vegetables": str(CATEGORY_TILE_DIR / "fruits_and_vegetables.jpg"),
}

DEFAULT_TILE = str(CATEGORY_TILE_DIR / "default.jpg")
CATEGORY_PIE_COLORS = [
    "#6F5CFF", "#4B3AD5", "#2F6BFF", "#F4C84E", "#48B26B",
    "#FF8A80", "#A06CD5", "#2E86C1", "#F78FB3", "#7F8C8D",
]
PURPLE_SCALE = ["#D9D0FF", "#6F5CFF"]

def clean_html(html_str: str) -> str:
    if html_str is None:
        return ""
    return "\n".join(line.lstrip() for line in html_str.strip().splitlines())

def display_value(value):
    if value is None:
        return "-"
    if isinstance(value, float) and math.isnan(value):
        return "-"
    text = str(value).strip()
    if text in {"", "N/A", "nan", "None"}:
        return "-"
    return text

producer_csv_path = Path("malta_producers.csv")
creators_csv_path = Path("local_market_creators.csv")
trends_csv_path = Path("local_market_trends.csv")
demographics_csv_path = Path("malta_neighbourhood_demographics.csv")

if not producer_csv_path.exists():
    st.error("malta_producers.csv was not found in the project folder.")
    st.stop()

df = pd.read_csv(producer_csv_path).fillna("N/A")
df["Latitude_num"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude_num"] = pd.to_numeric(df["Longitude"], errors="coerce")

if creators_csv_path.exists():
    creators_df = pd.read_csv(creators_csv_path).fillna("N/A")
else:
    creators_df = pd.DataFrame()

if trends_csv_path.exists():
    trends_df = pd.read_csv(trends_csv_path).fillna("N/A")
else:
    trends_df = pd.DataFrame()

if demographics_csv_path.exists():
    demographics_df = pd.read_csv(demographics_csv_path).fillna("N/A")
else:
    demographics_df = pd.DataFrame()

st.title("Hyperlocal & Trend Range Analytics")
st.caption("Interactive sourcing dashboard for local producers across Malta.")

st.info("""
**Key Updates for Malta:**
- Map configured for Valletta, Malta (center: 35.9375, 14.3754)
- Zoom level set to 10
- CSV files updated to: malta_producers.csv and malta_neighbourhood_demographics.csv
- All references changed from London to Malta
- Currency set to EUR (€)
""")

if not df.empty:
    st.subheader("Producer Count")
    st.metric("Total Producers", len(df))

    filtered_map_df = df.dropna(subset=["Latitude_num", "Longitude_num"]).copy()
    if not filtered_map_df.empty:
        map_counts = (
            filtered_map_df
            .groupby(["Neighbourhood", "Latitude_num", "Longitude_num"], as_index=False)
            .agg(Producer_Count=("Producer", "count"))
        )
        map_counts["bubble_size"] = map_counts["Producer_Count"] * 6
        map_counts["label"] = map_counts["Producer_Count"].astype(str)

        fig_map = px.scatter_mapbox(
            map_counts,
            lat="Latitude_num",
            lon="Longitude_num",
            size="bubble_size",
            size_max=45,
            color="Producer_Count",
            color_continuous_scale=PURPLE_SCALE,
            labels={"Producer_Count": "Producer Count"},
            hover_name="Neighbourhood",
            hover_data={
                "Producer_Count": True,
                "Latitude_num": False,
                "Longitude_num": False,
                "bubble_size": False,
            },
            text="label",
            zoom=10,
            center={"lat": 35.9375, "lon": 14.3754},
            height=520,
        )
        fig_map.update_traces(
            textposition="middle center",
            textfont=dict(size=18, color="white"),
            opacity=0.45,
        )
        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin=dict(r=0, t=0, l=0, b=0),
            coloraxis_colorbar=dict(title="Producer Count"),
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True})
else:
    st.warning("No producer data loaded. Please ensure malta_producers.csv is in the project folder.")
