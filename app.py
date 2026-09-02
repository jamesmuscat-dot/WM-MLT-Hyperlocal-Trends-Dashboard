import base64
import html
import math
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Wolt Market · Hyperlocal Range",
    layout="wide",
)

# -----------------------
# WOLT MARKET BRAND
# Digital palette from Bynder. Type: Omnes Black (headlines),
# Omnes Regular/Semibold (body). Tracking 0, leading 1.2 × size.
# Hand type only for short wishes. Drop Omnes files in assets/fonts/.
# -----------------------
WM_AVOCADO = "#0f3310"
WM_LIME = "#a1ce47"
WM_PAPER = "#d6ba97"
WM_LIGHT_PAPER = "#f6f0e9"
WM_LIGHT_LIME = "#d1f694"
WM_WHITE = "#ffffff"  # brand: paper bags use white
WM_GREEN = WM_AVOCADO
WM_GREEN_DEEP = WM_AVOCADO
WM_SAGE = WM_LIME
WM_LEAF = WM_LIME
WM_CREAM = WM_LIGHT_PAPER
WM_CREAM_2 = WM_PAPER
WM_MINT = WM_LIGHT_LIME
WM_MUTED = WM_AVOCADO
WM_MUTED_2 = WM_AVOCADO
WM_INK = WM_AVOCADO
WM_BORDER = WM_PAPER
WM_PEACH = WM_PAPER
FONT_DIR = Path("assets/fonts")
FONT_HEAD = '"Omnes Black", Omnes, Nunito, "Nunito Sans", sans-serif'
FONT_BODY = '"Omnes Regular", Omnes, Nunito, "Nunito Sans", sans-serif'
FONT_SEMI = '"Omnes Semibold", Omnes, Nunito, "Nunito Sans", sans-serif'
FONT_HAND = '"Wolt Market Hand", "WoltMarketHand", Caveat, "Segoe Script", cursive'


def _font_file(*names: str) -> Optional[Path]:
    for name in names:
        path = FONT_DIR / name
        if path.exists():
            return path
    return None


def _font_face(family: str, weight: int, path: Path) -> str:
    ext = path.suffix.lower()
    fmt = {".woff2": "woff2", ".woff": "woff", ".otf": "opentype", ".ttf": "truetype"}.get(ext, "truetype")
    mime = {
        ".woff2": "font/woff2",
        ".woff": "font/woff",
        ".otf": "font/otf",
        ".ttf": "font/ttf",
    }.get(ext, "font/ttf")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        f"@font-face{{font-family:'{family}';src:url(data:{mime};base64,{data}) "
        f"format('{fmt}');font-weight:{weight};font-style:normal;font-display:swap;}}"
    )


def _brand_font_css() -> str:
    faces = []
    files = [
        ("Omnes Black", 900, ("Omnes-Black.woff2", "OmnesBlack.woff2", "Omnes-Black.otf", "Omnes-Black.ttf")),
        ("Omnes Regular", 400, ("Omnes-Regular.woff2", "OmnesRegular.woff2", "Omnes-Regular.otf", "Omnes-Regular.ttf")),
        ("Omnes Semibold", 600, ("Omnes-Semibold.woff2", "Omnes-SemiBold.woff2", "OmnesSemibold.woff2", "Omnes-Semibold.otf")),
        ("Omnes", 400, ("Omnes.woff2", "Omnes.otf", "Omnes.ttf")),
        ("Wolt Market Hand", 500, ("WoltMarketHand.woff2", "Wolt-Market-Hand.woff2", "WM-Hand.woff2", "WoltMarketHand.otf")),
    ]
    for family, weight, names in files:
        path = _font_file(*names)
        if path:
            faces.append(_font_face(family, weight, path))
    google = (
        "@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600"
        "&family=Nunito:wght@400;600;800;900&display=swap');\n"
        if not faces
        else ""
    )
    # Always keep Nunito/Caveat as fallback if only some Omnes weights are present.
    if faces:
        google = (
            "@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600"
            "&family=Nunito:wght@400;600;800;900&display=swap');\n"
        )
    return google + "".join(faces)


st.markdown(
    f"""
    <style>
        {_brand_font_css()}
        :root {{
            --wm-avocado: {WM_AVOCADO};
            --wm-lime: {WM_LIME};
            --wm-paper: {WM_PAPER};
            --wm-light-paper: {WM_LIGHT_PAPER};
            --wm-light-lime: {WM_LIGHT_LIME};
            --wm-green: {WM_GREEN};
            --wm-cream: {WM_CREAM};
            --wm-white: {WM_WHITE};
            --wm-mint: {WM_MINT};
            --wm-muted: {WM_MUTED};
            --wm-border: {WM_BORDER};
            --wm-font-head: {FONT_HEAD};
            --wm-font-body: {FONT_BODY};
            --wm-font-semi: {FONT_SEMI};
            --wm-font-hand: {FONT_HAND};
        }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        html, body, [class*="st-"], .stApp, .stMarkdown, p, label, span, div {{
            font-family: {FONT_BODY} !important;
            letter-spacing: 0 !important;
        }}
        .stApp {{
            background: {WM_CREAM} !important;
            color: {WM_GREEN} !important;
        }}
        [data-testid="stHeader"] {{
            background: {WM_CREAM} !important;
        }}
        .block-container {{
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1600px;
        }}
        h1, h2, h3, h4,
        [data-testid="stHeading"] h1,
        [data-testid="stHeading"] h2,
        [data-testid="stHeading"] h3,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            font-family: {FONT_HEAD} !important;
            font-weight: 900 !important;
            color: {WM_GREEN} !important;
            letter-spacing: 0 !important;
            line-height: 1.2 !important;
        }}
        p, li, label, .stCaption, [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"] p {{
            font-family: {FONT_BODY} !important;
            color: {WM_INK};
            line-height: 1.2 !important;
            letter-spacing: 0 !important;
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {WM_MUTED} !important;
        }}
        [data-testid="stSidebar"] {{
            background: {WM_WHITE} !important;
            border-right: 1px solid {WM_BORDER};
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {{
            font-family: {FONT_HEAD} !important;
            color: {WM_GREEN} !important;
        }}
        div[data-testid="stTabs"] {{
            margin-top: 0 !important;
            position: relative;
            z-index: 10;
        }}
        button[data-baseweb="tab"] {{
            font-family: {FONT_SEMI} !important;
            font-weight: 600 !important;
            color: {WM_MUTED} !important;
            letter-spacing: 0 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {WM_GREEN} !important;
        }}
        [data-baseweb="tab-highlight"],
        [data-baseweb="tab-border"] {{
            background-color: {WM_GREEN} !important;
            border-color: {WM_GREEN} !important;
        }}
        .stButton > button, .stDownloadButton > button, .stLinkButton > a {{
            font-family: {FONT_SEMI} !important;
            font-weight: 600 !important;
            background: {WM_GREEN} !important;
            color: {WM_CREAM} !important;
            border: 0 !important;
            border-radius: 999px !important;
            letter-spacing: 0 !important;
        }}
        .stButton > button:hover, .stLinkButton > a:hover {{
            background: {WM_LIME} !important;
            color: {WM_AVOCADO} !important;
        }}
        [data-testid="stMetricValue"] {{
            font-family: {FONT_HEAD} !important;
            color: {WM_GREEN} !important;
        }}
        [data-testid="stDataFrame"], [data-testid="stTable"] {{
            font-family: {FONT_BODY} !important;
        }}
        .wm-hand {{
            font-family: {FONT_HAND} !important;
            font-size: 28px;
            font-weight: 500;
            color: {WM_GREEN};
            line-height: 1.2;
            letter-spacing: 0;
            transform: rotate(-3deg);
            display: inline-block;
            margin: 4px 0 10px 2px;
        }}
        div[data-testid="stAlert"] {{
            background: {WM_MINT};
            border: 1px solid {WM_BORDER};
            color: {WM_GREEN};
        }}
        [data-testid="stExpander"] {{
            background: {WM_WHITE};
            border: 1px solid {WM_BORDER};
            border-radius: 16px;
        }}
        [data-baseweb="select"] > div,
        [data-baseweb="input"] {{
            background-color: {WM_WHITE} !important;
            border-color: {WM_BORDER} !important;
        }}
        [data-testid="stCheckbox"] label p,
        [data-testid="stRadio"] label p {{
            font-family: {FONT_BODY} !important;
            color: {WM_GREEN} !important;
        }}
        .stSlider [role="slider"] {{
            background-color: {WM_GREEN} !important;
        }}
        div[data-testid="stFileUploader"] {{
            background: {WM_WHITE};
            border: 1px dashed {WM_BORDER};
            border-radius: 16px;
        }}
        .stMarkdown div[style*="font-weight:800"],
        .stMarkdown div[style*="font-weight: 800"],
        .stMarkdown div[style*="font-weight:900"] {{
            font-family: {FONT_HEAD} !important;
        }}
        .stMarkdown div[style*="font-weight:700"],
        .stMarkdown div[style*="font-weight: 700"],
        .stMarkdown div[style*="font-weight:600"] {{
            font-family: {FONT_SEMI} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# CONSTANTS
# -----------------------
MAP_HEIGHT = 520
CHART_HEIGHT = 320
TOP_ROW_GAP = 14
SECTION_GAP = 12
MARKET_NAME = "Wolt Market"
MAP_CENTER = {"lat": 50.0, "lon": 15.0}
MAP_ZOOM = 4
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
    "Bakery": str(CATEGORY_TILE_DIR / "bakeries.jpg"),
    "Coffee Roasteries": str(CATEGORY_TILE_DIR / "coffee_roasteries.jpg"),
    "Coffee Roastery": str(CATEGORY_TILE_DIR / "coffee_roasteries.jpg"),
    "Breweries": str(CATEGORY_TILE_DIR / "breweries.jpg"),
    "Brewery": str(CATEGORY_TILE_DIR / "breweries.jpg"),
    "Distilleries": str(CATEGORY_TILE_DIR / "distilleries.jpg"),
    "Delicatessen": str(CATEGORY_TILE_DIR / "delicatessen.jpg"),
    "Butcher Shops": str(CATEGORY_TILE_DIR / "butcher_shops.jpg"),
    "Butcher Shop": str(CATEGORY_TILE_DIR / "butcher_shops.jpg"),
    "Seafood Producers": str(CATEGORY_TILE_DIR / "seafood_producers.jpg"),
    "Local Soft Drinks": str(CATEGORY_TILE_DIR / "local_soft_drinks.jpg"),
    "Soft Drinks": str(CATEGORY_TILE_DIR / "local_soft_drinks.jpg"),
    "Local Snacks": str(CATEGORY_TILE_DIR / "local_snacks.jpg"),
    "Fruits & Vegetables": str(CATEGORY_TILE_DIR / "fruits_and_vegetables.jpg"),
}
DEFAULT_TILE = str(CATEGORY_TILE_DIR / "default.jpg")
TREND_IMAGE_KEYWORDS = [
    (["vegan", "plant-based", "plant based", "tofu", "oat milk", "alpro"], "vegan_plant_based.png"),
    (["kefir", "probiotic", "kombucha", "kimchi", "prebiotic"], "gut_health.png"),
    (["sourdough", "organic bread", "artisan bread"], "sourdough.png"),
    (["seacuterie", "tinned fish", "canned fish", "sardine", "anchovy", "ventresca"], "tinned_fish.png"),
    (["halloumi"], "halloumi.png"),
    (["laiki"], "laiki_produce.png"),
    (["pivo", "craft beer"], "craft_beer.png"),
    (["loukoumi", "lokum", "geroskipou"], "loukoumi.png"),
    (["qatiq", "qatıq", "pendir"], "village_dairy.png"),
    (["qutab", "dolma", "plov", "tandir"], "national_dishes.png"),
    (["savalan", "brandy", "chabiant"], "wine_brandy.png"),
    (["caviar", "sturgeon", "smoked fish"], "caviar.png"),
    (["coffee", "cold brew", "espresso", "lot61"], "specialty_coffee.png"),
    (["wine"], "wine_brandy.png"),
]
TREND_CATEGORY_FALLBACKS = [
    (["coffee"], "Coffee Roastery"),
    (["sourdough", "bread", "bakery"], "Bakery"),
    (["pivo", "craft beer", "brewery"], "Brewery"),
    (["wine", "brandy"], "Distilleries"),
    (["sardine", "anchovy", "caviar", "sturgeon", "seafood", "fish"], "Seafood Producers"),
    (["laiki", "produce", "vegetable", "fruit"], "Fruits & Vegetables"),
    (["loukoumi", "snack"], "Local Snacks"),
    (["halloumi", "dairy", "pendir", "qatiq", "kefir", "yogurt"], "Delicatessen"),
    (["vegan", "plant-based", "tofu"], "Fruits & Vegetables"),
]
CATEGORY_PIE_COLORS = [
    "#0f3310",
    "#a1ce47",
    "#d6ba97",
    "#d1f694",
    "#0f3310",
    "#a1ce47",
    "#d6ba97",
    "#d1f694",
    "#0f3310",
    "#a1ce47",
]
BRAND_SCALE = ["#d1f694", "#0f3310"]
PURPLE_SCALE = BRAND_SCALE  # charts still pass this name
px.defaults.color_discrete_sequence = CATEGORY_PIE_COLORS

# -----------------------
# INLINE SVG ICONS (no external image files needed)
# -----------------------
def _svg(path_markup: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'width="26" height="26" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f"{path_markup}</svg>"
    )

ICON_USERS = _svg(
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
    '<circle cx="9" cy="7" r="4"/>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
    '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
)
ICON_USER_GROUP = _svg(
    '<circle cx="8" cy="8" r="3"/>'
    '<circle cx="16" cy="8" r="3"/>'
    '<path d="M2 20c0-3 2.5-5 6-5s6 2 6 5"/>'
    '<path d="M12 20c.3-2.6 2.4-4.5 5-4.5 2.9 0 5 2 5 4.5"/>'
)
ICON_TRENDING_UP = _svg(
    '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
    '<polyline points="16 7 22 7 22 13"/>'
)
ICON_LIGHTBULB = _svg(
    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1.3.5 2.6 1.5 3.5.8.8 1.3 1.5 1.5 2.5"/>'
    '<path d="M9 18h6"/>'
    '<path d="M10 22h4"/>'
)
ICON_SEARCH = _svg(
    '<circle cx="11" cy="11" r="8"/>'
    '<path d="m21 21-4.3-4.3"/>'
)
ICON_MAP_PIN = _svg(
    '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>'
    '<circle cx="12" cy="10" r="3"/>'
)
ICON_GRID = _svg(
    '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
    '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
    '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
    '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
)
ICON_MAP = _svg(
    '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3Z"/>'
    '<path d="M9 3v15"/>'
    '<path d="M15 6v15"/>'
)
ICON_FILE_TEXT = _svg(
    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
    '<polyline points="15 2 15 7 20 7"/>'
    '<line x1="9" y1="13" x2="15" y2="13"/>'
    '<line x1="9" y1="17" x2="15" y2="17"/>'
)
ICON_CLIPBOARD_COPY = _svg(
    '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
)
ICON_CLOUD_UPLOAD = _svg(
    '<path d="M12 13v8"/>'
    '<path d="m8 17 4-4 4 4"/>'
    '<path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 4 16.29"/>'
)
ICON_LINK = _svg(
    '<path d="M9 17H7A5 5 0 0 1 7 7h2"/>'
    '<path d="M15 7h2a5 5 0 1 1 0 10h-2"/>'
    '<line x1="8" y1="12" x2="16" y2="12"/>'
)
ICON_SPARKLES = _svg(
    '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.937A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>'
    '<path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>'
)


# -----------------------
# HELPERS
# -----------------------
def clean_html(html_str: str) -> str:
    """Strip leading whitespace per line so Streamlit's markdown/CommonMark
    parser doesn't mistake indented HTML for a code block (4+ leading
    spaces on a line triggers CommonMark's 'indented code block' rule and
    the HTML gets rendered as literal text instead of parsed as markup).
    """
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


def _choice_values(series) -> list:
    if series is None:
        return []
    vals = series.dropna().astype(str).str.strip()
    vals = vals[~vals.str.lower().isin({"", "n/a", "nan", "none"})]
    return sorted(vals.unique().tolist())


def esc(value):
    return html.escape(display_value(value))


def is_valid_link(value):
    text = str(value).strip()
    return text.startswith("http://") or text.startswith("https://")


def safe_followers_text(value):
    text = str(value).strip()
    if text in {"", "N/A", "nan", "None"}:
        return "-"
    try:
        num = pd.to_numeric(text.replace(",", ""), errors="coerce")
        if pd.isna(num):
            return "-"
        return f"{int(num):,}"
    except Exception:
        return "-"


def resolve_image_source(source):
    if not source:
        return None
    source = str(source).strip()
    if source.startswith("http://") or source.startswith("https://"):
        return source
    path = Path(source)
    if path.exists():
        return str(path)
    if Path(DEFAULT_TILE).exists():
        return DEFAULT_TILE
    return None


def image_path_to_data_uri(image_path):
    if not image_path:
        return None
    path = Path(image_path)
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = "image/jpeg"
    if suffix == ".png":
        mime = "image/png"
    elif suffix == ".webp":
        mime = "image/webp"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def get_display_image(row):
    photo_url = str(row.get("Photo URL", "N/A")).strip()
    if photo_url and photo_url != "N/A":
        resolved = resolve_image_source(photo_url)
        if resolved:
            return resolved
    category = str(row.get("Category", "DEFAULT")).strip()
    candidate = CATEGORY_TILES.get(category, DEFAULT_TILE)
    resolved = resolve_image_source(candidate)
    if resolved:
        return resolved
    return None


def top_metric_card(label, value, subtitle, icon=None, icon_bg="#d1f694", icon_color="#0f3310", value_color="#0f3310", card_bg="#ffffff"):
    icon_html = ""
    if icon:
        icon_html = f"""
            <div style="
                width: 56px;
                height: 56px;
                min-width: 56px;
                border-radius: 14px;
                background: {icon_bg};
                color: {icon_color};
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            ">{icon}</div>
        """
    return f"""
    <div style="
        background: {card_bg};
        border-radius: 16px;
        border: 1px solid #d6ba97;
        box-shadow: 0 8px 20px rgba(15, 51, 16, 0.06);
        padding: 16px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        height: 116px;
        overflow: hidden;
    ">
        {icon_html}
        <div style="min-width: 0;">
            <div style="font-size: 13px; color: #0f3310; margin-bottom: 6px; font-weight: 600;">
                {esc(label)}
            </div>
            <div style="font-size: 28px; line-height: 1.2; font-weight: 900; color: {value_color};">
                {esc(value)}
            </div>
            <div style="font-size: 12px; color: #0f3310; margin-top: 6px;">
                {esc(subtitle)}
            </div>
        </div>
    </div>
    """


def stat_card(label, value):
    return f"""
    <div style="
        background: #ffffff;
        border-radius: 14px;
        padding: 10px 12px;
        margin-bottom: 8px;
        box-shadow: 0 8px 18px rgba(15, 51, 16, 0.06);
    ">
        <div style="font-size: 12px; color: #0f3310; margin-bottom: 6px;">{esc(label)}</div>
        <div style="font-size: 22px; font-weight: 900; line-height: 1.2; color:#0f3310;">{esc(value)}</div>
    </div>
    """


def _numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype="float64")
    return pd.to_numeric(df[col], errors="coerce")


def _clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def _minmax_score(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    if s.notna().sum() == 0:
        return pd.Series(0.0, index=s.index, dtype="float64")
    s = s.fillna(s.median())
    denom = s.max() - s.min()
    if pd.isna(denom) or denom == 0:
        return pd.Series(0.5, index=s.index, dtype="float64")
    return (s - s.min()) / denom


def build_producer_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rating = _numeric_series(out, "Google Rating")
    reviews = _numeric_series(out, "Google Reviews")
    insta = _numeric_series(out, "Instagram Followers")
    tiktok = _numeric_series(out, "TikTok Followers")
    rating_norm = _minmax_score(rating.fillna(rating.median()))
    review_norm = _minmax_score(np.log1p(reviews.fillna(0)))
    social_raw = np.log1p(insta.fillna(0) + tiktok.fillna(0))
    social_norm = _minmax_score(social_raw)
    hidden_reviews = reviews.fillna(reviews.max() if reviews.notna().any() else 0)
    hidden_review_norm = _minmax_score(np.log1p(hidden_reviews))
    hidden_gems_norm = 0.80 * rating_norm + 0.20 * (1 - hidden_review_norm)
    out["Overall Rank Score"] = (0.60 * review_norm + 0.30 * rating_norm + 0.10 * social_norm) * 100
    out["Most Popular Score"] = (0.90 * review_norm + 0.10 * rating_norm) * 100
    out["Highest Quality Score"] = (0.80 * rating_norm + 0.20 * review_norm) * 100
    out["Social Buzz Score"] = (0.70 * social_norm + 0.20 * review_norm + 0.10 * rating_norm) * 100
    out["Hidden Gems Score"] = hidden_gems_norm * 100
    return out


def resolve_creator_pic(name_handle: str):
    if not name_handle:
        return None
    import re
    raw = str(name_handle).strip()
    match = re.search(r"@([A-Za-z0-9._]+)", raw)
    candidates = []
    if match:
        handle = match.group(1)
        candidates.extend(
            [
                PROFILE_PIC_DIR / f"@{handle}.jpg",
                PROFILE_PIC_DIR / f"@{handle}.jpeg",
                PROFILE_PIC_DIR / f"@{handle}.png",
            ]
        )
    normalized = raw.lower().replace(" ", "_")
    candidates.extend(
        [
            PROFILE_PIC_DIR / f"{normalized}.jpg",
            PROFILE_PIC_DIR / f"{normalized}.jpeg",
            PROFILE_PIC_DIR / f"{normalized}.png",
        ]
    )
    for path in candidates:
        if path.exists():
            return str(path)
    return None


def resolve_trend_image(image_value, trend_row=None):
    """Resolve a circular thumbnail for a trend card.

    Order: Image column (path or URL) → assets/trend_images filename →
    keyword match on trend name / Search Keywords → category tile → default.
    """
    def _existing(path):
        p = Path(path) if path else None
        return str(p) if p is not None and p.exists() else None

    text = str(image_value or "").strip()
    if text not in {"", "N/A", "nan", "None"}:
        if text.startswith("http://") or text.startswith("https://"):
            return text
        for candidate in (
            Path(text),
            TREND_IMAGE_DIR / text,
            TREND_IMAGE_DIR / Path(text).name,
        ):
            found = _existing(candidate)
            if found:
                return found
        stem = Path(text).stem
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            found = _existing(TREND_IMAGE_DIR / f"{stem}{ext}")
            if found:
                return found

    haystack = ""
    if trend_row is not None:
        haystack = " ".join(
            [
                str(trend_row.get("Trend", "")),
                str(trend_row.get("Search Keywords", "")),
            ]
        ).lower()

    for needles, filename in TREND_IMAGE_KEYWORDS:
        if any(needle in haystack for needle in needles):
            found = _existing(TREND_IMAGE_DIR / filename)
            if found:
                return found
            stem = Path(filename).stem
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                found = _existing(TREND_IMAGE_DIR / f"{stem}{ext}")
                if found:
                    return found
            break

    for needles, category in TREND_CATEGORY_FALLBACKS:
        if any(needle in haystack for needle in needles):
            found = _existing(CATEGORY_TILES.get(category, DEFAULT_TILE))
            if found:
                return found
            break

    return _existing(DEFAULT_TILE)


def primary_platform(platform: str) -> str:
    p = str(platform).lower()
    if "tiktok" in p and "instagram" not in p:
        return "TikTok"
    return "Instagram"


def render_platform_icons_html(platform_value) -> str:
    """Render Instagram/TikTok logo icons for a Platform cell (e.g. 'Instagram',
    'TikTok', or 'Instagram / TikTok'). Falls back to plain text for anything
    that doesn't match a known platform or if the icon file is missing.
    """
    import re
    text = display_value(platform_value)
    if text == "-":
        return "-"

    names = [p.strip() for p in re.split(r"[/,&]", text) if p.strip()]
    icons_html = []
    for name in names:
        lname = name.lower()
        key = None
        if "insta" in lname:
            key = "Instagram"
        elif "tiktok" in lname or "tik tok" in lname:
            key = "TikTok"

        icon_uri = None
        if key and key in PLATFORM_ICON_FILES:
            icon_uri = image_path_to_data_uri(PLATFORM_ICON_FILES[key])

        if icon_uri:
            icons_html.append(
                f'<img src="{icon_uri}" alt="{html.escape(key)}" title="{html.escape(key)}" '
                f'style="width:40px; height:40px; border-radius:10px; object-fit:cover; '
                f'box-shadow:0 3px 8px rgba(15, 51, 16, 0.08);">'
            )
        else:
            icons_html.append(f'<span style="font-size:13px; color:#0f3310;">{html.escape(name)}</span>')

    if not icons_html:
        return html.escape(text)

    return (
        '<div style="display:flex; align-items:center; gap:6px;">'
        + "".join(icons_html)
        + "</div>"
    )


def content_bucket(content_focus: str) -> str:
    s = str(content_focus).lower()
    rules = [
        ("Recipes & Cooking", ["recipe", "cook", "dinner", "pantry", "home cooking", "easy recipes", "weeknight"]),
        ("Food Discovery", ["discovery", "restaurant", "guide", "pop-up", "café", "cafe", "trips", "food reviewing", "roundups"]),
        ("Lifestyle & Travel", ["lifestyle", "travel", "hotel", "destination", "luxury"]),
        ("Healthy / Functional", ["protein", "healthy", "functional", "high-protein", "plant-only", "fitness"]),
    ]
    for label, keywords in rules:
        if any(k in s for k in keywords):
            return label
    return "Other"


def strength_score_label(value):
    s = str(value).strip().lower()
    if s in {"medium-strong", "medium strong"}:
        return "Medium-strong"
    if s == "strong":
        return "Strong"
    if s == "medium":
        return "Medium"
    return "Other"


def strength_chip_style(strength):
    s = str(strength).strip().lower()
    if s in {"medium-strong", "medium strong"}:
        return "background:#fff1e6;color:#f97316;"
    if s == "strong":
        return "background:#d1f694;color:#0f3310;"
    if s == "medium":
        return "background:#fff7e6;color:#f59e0b;"
    return "background:#d1f694;color:#0f3310;"


SEARCH_VALIDATED_MIN = 200
SEARCH_WEAK_MIN = 30

# Used when the live GitHub trends file is still the old format without a
# Search Keywords column. The spreadsheet remains the source of truth when
# that column is present.
DEFAULT_SEARCH_KEYWORDS = {
    ("MLT", 1): "vegan; plant-based; plant based; oat milk; almond milk; soy milk; tofu; dairy free; dairy-free; alpro; oatly; seitan; meat free",
    ("MLT", 2): "kefir; probiotic; prebiotic; kombucha; kimchi",
    ("MLT", 3): "sourdough; organic bread; artisan bread",
    ("MLT", 4): "seacuterie; tinned fish; canned fish; sardine; sardines; anchovy; anchovies; ventresca",
    ("MLT", 5): "coffee; cold brew; lot61; lot 61; espresso; coffee beans",
    ("CYP", 1): "halloumi",
    ("CYP", 2): "laiki",
    ("CYP", 3): "coffee",
    ("CYP", 4): "pivo; craft beer",
    ("CYP", 5): "loukoumi; geroskipou; lokum",
    ("AZE", 1): "qatiq; qatıq; pendir; yogurt; yoghurt",
    ("AZE", 2): "qutab; dolma; plov; tandir",
    ("AZE", 3): "coffee; sensum",
    ("AZE", 4): "savalan; wine; brandy; chabiant",
    ("AZE", 5): "caviar; sturgeon; smoked fish",
}


def _keywords_from_text(raw) -> list:
    if str(raw).strip() in {"", "N/A", "nan", "None"}:
        return []
    return [p.strip().lower() for p in re.split(r"[;|,]", str(raw)) if p.strip()]


def parse_search_keywords(row) -> list:
    raw = ""
    if hasattr(row, "index"):
        for key in row.index:
            normalized = str(key).replace("\ufeff", "").strip().lower().replace("_", " ")
            if normalized == "search keywords":
                raw = row[key]
                break
    elif hasattr(row, "get"):
        raw = row.get("Search Keywords", "")
    found = _keywords_from_text(raw)
    if found:
        return found
    country = str(row.get("Country", "")).strip() if hasattr(row, "get") else ""
    rank = pd.to_numeric(row.get("Rank", 0), errors="coerce") if hasattr(row, "get") else 0
    rank_i = int(rank) if pd.notna(rank) else 0
    return _keywords_from_text(DEFAULT_SEARCH_KEYWORDS.get((country, rank_i), ""))


def validation_chip_style(status: str) -> str:
    s = str(status).strip().lower()
    if s == "validated":
        return "background:#d1f694;color:#0f3310;"
    if s == "weak signal":
        return "background:#fff1e6;color:#c2410c;"
    if s == "not in search":
        return "background:#f6f0e9;color:#0f3310;"
    return "background:#f6f0e9;color:#0f3310;"


def validate_trend_against_search(trend_row, search_df: pd.DataFrame) -> dict:
    keywords = parse_search_keywords(trend_row)
    country = str(trend_row.get("Country", "")).strip()
    empty = {
        "status": "No search data",
        "message": "No in-venue app search extract for this country yet.",
        "searches": 0,
    }
    if search_df is None or search_df.empty:
        return empty
    scoped = search_df
    if "Country" in search_df.columns and country:
        scoped = search_df[search_df["Country"].astype(str) == country]
    if scoped.empty:
        return empty
    if not keywords:
        return {
            "status": "No search data",
            "message": "Add Search Keywords on this trend to match it against app queries.",
            "searches": 0,
        }

    queries = scoped.copy()
    queries["QueryClean"] = queries["Query"].astype(str).str.split("?").str[0].str.strip()
    queries["QueryLower"] = queries["QueryClean"].str.lower()
    queries["Searches"] = pd.to_numeric(queries.get("Searches"), errors="coerce").fillna(0)

    mask = pd.Series(False, index=queries.index)
    for keyword in keywords:
        if " " in keyword:
            mask = mask | queries["QueryLower"].str.contains(
                re.escape(keyword), regex=True, na=False
            )
        else:
            mask = mask | queries["QueryLower"].str.contains(
                rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])",
                regex=True,
                na=False,
            )
    hits = queries.loc[mask]
    total = int(hits["Searches"].sum()) if not hits.empty else 0
    if hits.empty:
        top = []
    else:
        top_df = (
            hits.groupby("QueryLower", as_index=False)["Searches"]
            .sum()
            .sort_values("Searches", ascending=False)
            .head(3)
        )
        top = [
            (str(r["QueryLower"]), int(r["Searches"]))
            for _, r in top_df.iterrows()
        ]

    if total >= SEARCH_VALIDATED_MIN:
        status = "Validated"
        message = (
            f"Customers are searching this in the Wolt Market app — "
            f"{total:,} matching searches in the last 90 days."
        )
    elif total >= SEARCH_WEAK_MIN:
        status = "Weak signal"
        message = (
            f"Some app search, but not a habit yet — "
            f"{total:,} matching searches in the last 90 days."
        )
    elif total > 0:
        status = "Not in search"
        message = (
            f"Not a current search habit — only {total:,} matching searches "
            "in the last 90 days."
        )
    else:
        status = "Not in search"
        message = (
            "Not showing up in app search yet. Creator-led for now, "
            "not a current customer search habit."
        )
    if top:
        bits = ", ".join(f"“{q}” ({n:,})" for q, n in top)
        message += f" Top queries: {bits}."
    return {"status": status, "message": message, "searches": total}


def build_platform_split(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["Primary Platform"] = d["Platform"].apply(primary_platform)
    out = d["Primary Platform"].value_counts().reset_index()
    out.columns = ["Platform", "Count"]
    return out


def build_content_focus(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["Bucket"] = d["Content Focus"].apply(content_bucket)
    out = d["Bucket"].value_counts().reset_index()
    out.columns = ["Bucket", "Count"]
    order = ["Recipes & Cooking", "Food Discovery", "Lifestyle & Travel", "Healthy / Functional", "Other"]
    out["Bucket"] = pd.Categorical(out["Bucket"], categories=order, ordered=True)
    out = out.sort_values("Bucket")
    return out


def render_creator_table_html(df: pd.DataFrame) -> str:
    rows = []
    for _, row in df.iterrows():
        name_handle = display_value(row.get("Name / Handle"))
        name_part = name_handle
        handle_part = ""
        if " / @" in name_handle:
            name_part, handle_part = name_handle.split(" / @", 1)
            handle_part = "@" + handle_part
        elif " / " in name_handle:
            name_part, handle_part = name_handle.split(" / ", 1)
        profile_pic_path = resolve_creator_pic(name_handle)
        profile_pic_uri = image_path_to_data_uri(profile_pic_path) if profile_pic_path else None
        if profile_pic_uri:
            pic_html = f"""
                <img src="{profile_pic_uri}" style="
                    width:56px;
                    height:56px;
                    border-radius:999px;
                    object-fit:cover;
                    box-shadow:0 6px 14px rgba(15, 51, 16, 0.08);
                ">
            """
        else:
            pic_html = """
                <div style="
                    width:56px;
                    height:56px;
                    border-radius:999px;
                    background:#d1f694;
                "></div>
            """
        platform_html = render_platform_icons_html(row.get("Platform"))
        followers_txt = safe_followers_text(row.get("Followers", row.get("Followers_num", "-")))
        content_focus = display_value(row.get("Content Focus"))
        key_signals = display_value(row.get("Key Trend Signals"))
        example_link_raw = display_value(row.get("Example Link"))
        if is_valid_link(example_link_raw):
            example_link_html = (
                f'<a href="{html.escape(example_link_raw)}" target="_blank" rel="noopener noreferrer" '
                f'style="color:#0f3310; font-weight:600; text-decoration:none;">View profile ↗</a>'
            )
        else:
            example_link_html = html.escape(example_link_raw)
        rows.append(
            f"""
            <tr style="border-bottom:1px solid #d6ba97;">
                <td style="padding:14px 12px; width:84px; vertical-align:middle;">{pic_html}</td>
                <td style="padding:14px 12px; min-width:240px; vertical-align:middle;">
                    <div style="font-weight:700; color:#0f3310; line-height:1.2;">{html.escape(name_part)}</div>
                    <div style="font-size:13px; color:#0f3310; margin-top:3px;">{html.escape(handle_part)}</div>
                </td>
                <td style="padding:14px 12px; width:130px; vertical-align:middle;">{platform_html}</td>
                <td style="padding:14px 12px; width:120px; vertical-align:middle;">{html.escape(followers_txt)}</td>
                <td style="padding:14px 12px; min-width:230px; vertical-align:middle;">{html.escape(content_focus)}</td>
                <td style="padding:14px 12px; min-width:250px; vertical-align:middle;">{html.escape(key_signals)}</td>
                <td style="padding:14px 12px; width:160px; vertical-align:middle;">{example_link_html}</td>
            </tr>
            """
        )
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid #d6ba97;
        border-radius:16px;
        overflow:hidden;
        box-shadow:0 8px 18px rgba(15, 51, 16, 0.06);
    ">
        <div style="max-height:430px; overflow:auto;">
            <table style="
                width:100%;
                border-collapse:collapse;
                table-layout:fixed;
            ">
                <thead>
                    <tr style="
                        background:#ffffff;
                        color:#0f3310;
                        font-size:14px;
                        font-weight:700;
                        border-bottom:1px solid #d6ba97;
                    ">
                        <th style="padding:14px 12px; width:84px; text-align:left;">Profile Pic</th>
                        <th style="padding:14px 12px; min-width:240px; text-align:left;">Creator / Handle</th>
                        <th style="padding:14px 12px; width:130px; text-align:left;">Platform</th>
                        <th style="padding:14px 12px; width:120px; text-align:left;">Followers</th>
                        <th style="padding:14px 12px; min-width:230px; text-align:left;">Content Focus</th>
                        <th style="padding:14px 12px; min-width:250px; text-align:left;">Key Trend Signals</th>
                        <th style="padding:14px 12px; width:160px; text-align:left;">Example Link</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    </div>
    """


def build_trend_matching_prompt(trends_df: pd.DataFrame) -> str:
    """Build a ready-to-paste prompt for Claude/ChatGPT that lists whatever
    trends are currently loaded (from local_market_trends.csv), so the
    prompt text automatically updates if that file changes.
    """
    lines = [
        "You are helping a Wolt Market category manager decide which "
        f"candidate products to prioritise for dark-store listings in {MARKET_NAME}.",
        "",
        f"Here are the current emerging {MARKET_NAME} food & drink trends "
        "identified from local creator and social signals:",
        "",
    ]
    for _, row in trends_df.iterrows():
        rank_raw = pd.to_numeric(row.get("Rank", 0), errors="coerce")
        rank = int(rank_raw) if pd.notna(rank_raw) else "-"
        trend = display_value(row.get("Trend", ""))
        strength = strength_score_label(row.get("Strength", ""))
        desc = display_value(row.get("Description", ""))
        search_status = display_value(row.get("Search Status", ""))
        label = f"{rank}. {trend} (Strength: {strength}"
        if search_status not in {"", "N/A", "—", "-"}:
            label += f", App search: {search_status}"
        label += f") — {desc}"
        lines.append(label)

    lines += [
        "",
        "I will upload a candidate catalogue (CSV or Excel) of potential products or producers.",
        "For each candidate in the catalogue, please:",
        "1. Score how well it matches each trend above, from 0 to 100.",
        "2. Identify the single best-matching trend for each candidate.",
        "3. Give a one-sentence rationale for that match.",
        "4. Return a ranked shortlist of the strongest overall matches, sorted by match score.",
    ]
    return "\n".join(lines)


def render_catalogue_header_and_steps(trends_df: pd.DataFrame) -> str:
    step_icon_wrap = (
        "display:flex; align-items:center; justify-content:center; width:44px; height:44px; "
        "min-width:44px; border-radius:999px; background:#0f3310; color:white; flex-shrink:0;"
    )

    return f"""
    <div>
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="font-size:28px; font-weight:800; color:#0f3310;">Match Your Catalogue to These Trends</div>
            <div style="color:#0f3310;">{ICON_LINK}</div>
        </div>
        <div style="font-size:14px; color:#0f3310; margin-top:4px; margin-bottom:16px;">
            Use AI to match your candidate products to the latest food &amp; drink trends and get a ranked shortlist.
        </div>

        <div style="
            background:#ffffff; border:1px solid #d6ba97; border-radius:16px;
            box-shadow:0 8px 20px rgba(15, 51, 16, 0.06); padding:18px 22px; margin-bottom:16px;
            display:flex; align-items:center; justify-content:space-between; gap:10px;
        ">
            <div style="display:flex; align-items:center; justify-content:center; gap:14px; flex:1; min-width:0;">
                <div style="{step_icon_wrap}">{ICON_FILE_TEXT}</div>
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#0f3310; font-size:14px;">1. Copy the prompt</div>
                    <div style="font-size:12px; color:#0f3310; margin-top:2px;">We've prepared a detailed prompt with the latest trend insights.</div>
                </div>
            </div>
            <div style="color:#d6ba97; font-size:20px; padding:0 6px;">→</div>
            <div style="display:flex; align-items:center; justify-content:center; gap:14px; flex:1; min-width:0;">
                <div style="{step_icon_wrap}">{ICON_CLIPBOARD_COPY}</div>
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#0f3310; font-size:14px;">2. Paste into AI</div>
                    <div style="font-size:12px; color:#0f3310; margin-top:2px;">Open Claude or ChatGPT and paste the prompt.</div>
                </div>
            </div>
            <div style="color:#d6ba97; font-size:20px; padding:0 6px;">→</div>
            <div style="display:flex; align-items:center; justify-content:center; gap:14px; flex:1; min-width:0;">
                <div style="{step_icon_wrap}">{ICON_CLOUD_UPLOAD}</div>
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#0f3310; font-size:14px;">3. Upload your catalogue</div>
                    <div style="font-size:12px; color:#0f3310; margin-top:2px;">Upload your candidate catalogue (CSV or Excel) and get results.</div>
                </div>
            </div>
        </div>

        <div style="
            background:#d1f694; border:1px solid #d6ba97; border-bottom:none;
            border-radius:16px 16px 0 0; padding:14px 20px;
            display:flex; align-items:center; gap:8px; font-weight:700; color:#0f3310; font-size:17px;
        ">
            <span style="color:#0f3310;">{ICON_SPARKLES}</span>
            Prompt — copy and paste into Claude or ChatGPT
        </div>
    </div>
    """


def render_catalogue_footer() -> str:
    def _assistant_icon_html(name: str, fallback_bg: str, fallback_letter: str, zoom: float = 1.0, origin: str = "center") -> str:
        icon_uri = None
        path = ASSISTANT_ICON_FILES.get(name)
        if path:
            icon_uri = image_path_to_data_uri(path)
        if icon_uri:
            return f"""
                <div style="
                    width:40px; height:40px; min-width:40px; border-radius:999px;
                    background:#d1f694; display:flex; align-items:center; justify-content:center;
                    flex-shrink:0; overflow:hidden;
                ">
                    <img src="{icon_uri}" alt="{html.escape(name)}" style="
                        width:100%; height:100%; object-fit:cover; object-position:center;
                        transform:scale({zoom}); transform-origin:{origin};
                    ">
                </div>
            """
        return f"""
            <div style="
                width:40px; height:40px; border-radius:999px; background:{fallback_bg};
                color:white; display:flex; align-items:center; justify-content:center;
                font-weight:700; font-size:16px; flex-shrink:0;
            ">{fallback_letter}</div>
        """

    claude_icon_html = _assistant_icon_html("Claude", "#D97757", "C", zoom=1.0)
    gpt_icon_html = _assistant_icon_html("ChatGPT", "#10A37F", "G", zoom=2.3, origin="50% 43%")

    return f"""
    <div>
        <div style="background:#d1f694; border:1px solid #d6ba97; border-radius:16px; padding:16px 20px; text-align:center; margin-bottom:14px;">
            <div style="font-weight:700; color:#0f3310; font-size:15px;">Ready to get your ranked shortlist?</div>
            <div style="font-size:13px; color:#0f3310; margin-top:2px;">Choose your preferred AI assistant to continue.</div>
        </div>

        <div style="display:flex; gap:14px;">
            <a href="https://claude.ai/new" target="_blank" rel="noopener noreferrer" style="
                flex:1; display:flex; align-items:center; gap:12px; text-decoration:none;
                background:#ffffff; border:1px solid #d6ba97; border-radius:14px; padding:14px 16px;
                box-shadow:0 6px 16px rgba(15, 51, 16, 0.06);
            ">
                {claude_icon_html}
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#0f3310; font-size:14px;">Open in Claude</div>
                    <div style="font-size:12px; color:#0f3310; margin-top:2px;">Paste the prompt and upload your catalogue</div>
                </div>
            </a>
            <a href="https://chat.openai.com/" target="_blank" rel="noopener noreferrer" style="
                flex:1; display:flex; align-items:center; gap:12px; text-decoration:none;
                background:#ffffff; border:1px solid #d6ba97; border-radius:14px; padding:14px 16px;
                box-shadow:0 6px 16px rgba(15, 51, 16, 0.06);
            ">
                {gpt_icon_html}
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#0f3310; font-size:14px;">Open in ChatGPT</div>
                    <div style="font-size:12px; color:#0f3310; margin-top:2px;">Paste the prompt and upload your catalogue</div>
                </div>
            </a>
        </div>
    </div>
    """


def render_neighbourhood_demographic_card(row) -> str:
    recommendations = str(row.get("Product Recommendations", "")).strip()
    chips_html = ""
    if recommendations and recommendations != "N/A":
        chips = [c.strip() for c in recommendations.split(";") if c.strip()]
        chips_html = "".join(
            f"""<span style="
                display:inline-block; background:#d1f694; color:#0f3310;
                font-size:12px; font-weight:600; padding:5px 12px;
                border-radius:999px; margin:0 6px 6px 0;
            ">{html.escape(c)}</span>"""
            for c in chips
        )

    return f"""
    <div style="
        background:#ffffff; border:1px solid #d6ba97; border-radius:16px;
        box-shadow:0 8px 20px rgba(15, 51, 16, 0.06); padding:18px 22px; margin-bottom:8px;
    ">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <span style="color:#0f3310;">{ICON_MAP_PIN}</span>
            <div style="font-size:18px; font-weight:800; color:#0f3310;">
                {html.escape(display_value(row.get("Neighbourhood")))} — Who lives here
            </div>
        </div>
        <div style="font-size:14px; color:#0f3310; line-height:1.6; margin-bottom:12px;">
            {html.escape(display_value(row.get("Summary")))}
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:16px; margin-bottom:12px;">
            <div style="flex:1; min-width:180px;">
                <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:2px;">DOMINANT SEGMENTS</div>
                <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(row.get("Dominant Segments")))}</div>
            </div>
            <div style="flex:1; min-width:180px;">
                <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:2px;">NOTABLE COMMUNITIES</div>
                <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(row.get("Notable Communities")))}</div>
            </div>
            <div style="flex:1; min-width:180px;">
                <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:2px;">SPENDING PROFILE</div>
                <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(row.get("Spending Profile")))}</div>
            </div>
        </div>
        <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:6px;">SUGGESTED RANGE FOCUS</div>
        <div>{chips_html}</div>
        <div style="font-size:11px; color:#0f3310; margin-top:12px;">
            AI-researched overview — directional only, not verified statistics. Spot-check before using for sourcing decisions.
        </div>
    </div>
    """


def render_city_planning_card(city: str, status: str, country_name: str) -> str:
    if str(status).strip() == "Expansion":
        headline = f"No Wolt Market store in {city} yet"
        body = (
            f"This is a planning view for a possible first store in {city}. "
            f"There is no live dark store here, so Hyperlocal Range will not show ranged producers until a category manager adds them. "
            f"Use the city snapshot below plus {country_name} trends and in-app search (Local Market Trends tab) to judge demand before opening."
        )
        chip = "Expansion city"
        chip_style = "background:#FFF1E6;color:#C2410C;"
    elif str(status).strip() == "In range":
        headline = f"{city} is ranged from existing stores"
        body = (
            f"There is no Wolt Market store inside {city}, but local producers here are already on the ranging list for nearby catchments."
        )
        chip = "In range — no store in this city"
        chip_style = "background:#d1f694;color:#0f3310;"
    else:
        headline = f"{city} has a live Wolt Market store"
        body = f"Producers and catchments below are the current dark-store ranging set for {city}."
        chip = "Live store"
        chip_style = "background:#d1f694;color:#0f3310;"
    return f"""
    <div style="
        background:#f6f0e9; border:1px solid #d6ba97; border-radius:16px;
        padding:16px 20px; margin-bottom:8px;
    ">
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px;">
            <div style="font-size:16px; font-weight:800; color:#0f3310;">{html.escape(headline)}</div>
            <div style="display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; {chip_style}">{html.escape(chip)}</div>
        </div>
        <div style="font-size:14px; color:#0f3310; line-height:1.55;">{html.escape(body)}</div>
    </div>
    """


DEMOGRAPHIC_TAG_RULES = [
    ("Halal", ["Dietary Considerations"], ["halal"]),
    ("Vegan / Plant-based", ["Dietary Considerations"], ["vegan", "plant-based"]),
    ("Vegetarian", ["Dietary Considerations"], ["vegetarian"]),
    ("Kosher", ["Dietary Considerations"], ["kosher"]),
    ("Premium", ["Spending Profile"], ["premium"]),
    ("Budget-friendly", ["Spending Profile"], ["budget"]),
    ("Family-focused", ["Dominant Segments", "Age Life Stage Skew"], ["famil"]),
    ("Student-heavy", ["Student University Proximity"], ["high"]),
    ("Nightlife-heavy", ["Day Night Pattern"], ["nightlife"]),
]


def get_neighbourhood_tags(row) -> list:
    tags = []
    for tag_name, cols, keywords in DEMOGRAPHIC_TAG_RULES:
        combined = " ".join(str(row.get(c, "")) for c in cols).lower()
        if any(kw in combined for kw in keywords):
            tags.append(tag_name)
    return tags


def spending_bucket(spending_text) -> str:
    text = str(spending_text).lower()
    if "ultra" in text:
        return "Ultra-premium"
    if "premium" in text and "mixed" not in text and "budget" not in text:
        return "Premium"
    if "budget" in text and "mid" not in text and "premium" not in text:
        return "Budget"
    if "mid" in text and "premium" not in text and "budget" not in text:
        return "Mid-range"
    return "Mixed"


SPENDING_BUCKET_COLORS = {
    "Ultra-premium": "#0f3310",
    "Premium": "#a1ce47",
    "Mixed": "#d6ba97",
    "Mid-range": "#d1f694",
    "Budget": "#d6ba97",
}

# Illustrative only — not measured data. Placeholder brackets until real
# average order value (AOV) by neighbourhood is available to replace these.
SPENDING_BUCKET_BRACKETS = {
    "Ultra-premium": {"weekly": "€150+", "basket": "€45+"},
    "Premium": {"weekly": "€100–€150", "basket": "€35–€45"},
    "Mid-range": {"weekly": "€70–€100", "basket": "€25–€35"},
    "Budget": {"weekly": "€40–€70", "basket": "€15–€25"},
    "Mixed": {"weekly": "Spans multiple brackets", "basket": "—"},
}


def render_spend_bracket_legend() -> str:
    rows_html = "".join(
        f"""
        <tr style="border-bottom:1px solid #d6ba97;">
            <td style="padding:8px 6px;">
                <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{SPENDING_BUCKET_COLORS[tier]}; margin-right:8px;"></span>
                <span style="font-size:13px; font-weight:600; color:#0f3310;">{html.escape(tier)}</span>
            </td>
            <td style="padding:8px 6px; font-size:13px; color:#0f3310;">{html.escape(bracket["weekly"])}</td>
            <td style="padding:8px 6px; font-size:13px; color:#0f3310;">{html.escape(bracket["basket"])}</td>
        </tr>
        """
        for tier, bracket in SPENDING_BUCKET_BRACKETS.items()
    )
    return f"""
    <div>
        <table style="width:100%; border-collapse:collapse; margin-bottom:8px;">
            <thead>
                <tr style="border-bottom:1px solid #d6ba97;">
                    <th style="text-align:left; padding:6px; font-size:11px; color:#0f3310; font-weight:600;">TIER</th>
                    <th style="text-align:left; padding:6px; font-size:11px; color:#0f3310; font-weight:600;">WEEKLY FOOD SPEND</th>
                    <th style="text-align:left; padding:6px; font-size:11px; color:#0f3310; font-weight:600;">BASKET VALUE</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div style="font-size:11px; color:#0f3310;">
            Illustrative brackets, not measured — placeholders pending real average order value (AOV) data.
        </div>
    </div>
    """


CONFIDENCE_BADGE_STYLE = {
    "High": "background:#a1ce47; color:#0f3310;",
    "Medium-High": "background:#d1f694; color:#0f3310;",
    "Medium": "background:#FFF7E0; color:#F5A623;",
    "Low": "background:#FFE9E5; color:#E4572E;",
}


def render_neighbourhood_full_card(row) -> str:
    recommendations = str(row.get("Product Recommendations", "")).strip()
    chips_html = ""
    if recommendations and recommendations != "N/A":
        chips = [c.strip() for c in recommendations.split(";") if c.strip()]
        chips_html = "".join(
            f"""<span style="
                display:inline-block; background:#d1f694; color:#0f3310;
                font-size:12px; font-weight:600; padding:5px 12px;
                border-radius:999px; margin:0 6px 6px 0;
            ">{html.escape(c)}</span>"""
            for c in chips
        )

    tags = get_neighbourhood_tags(row)
    tags_html = "".join(
        f"""<span style="
            display:inline-block; background:#d1f694; color:#0f3310;
            font-size:11px; font-weight:700; padding:4px 10px;
            border-radius:999px; margin:0 6px 6px 0; border:1px solid #d6ba97;
        ">{html.escape(t)}</span>"""
        for t in tags
    )

    confidence = display_value(row.get("Confidence"))
    confidence_style = CONFIDENCE_BADGE_STYLE.get(confidence, "background:#d1f694; color:#0f3310;")

    detail_fields = [
        ("AGE / LIFE-STAGE SKEW", row.get("Age Life Stage Skew")),
        ("STUDENT / UNIVERSITY PROXIMITY", row.get("Student University Proximity")),
        ("DAY / NIGHT PATTERN", row.get("Day Night Pattern")),
        ("DIETARY CONSIDERATIONS", row.get("Dietary Considerations")),
    ]
    detail_html = "".join(
        f"""
        <div style="flex:1; min-width:200px; margin-bottom:12px;">
            <div style="font-size:11px; color:#0f3310; font-weight:600; margin-bottom:2px;">{label}</div>
            <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(value))}</div>
        </div>
        """
        for label, value in detail_fields
    )

    return f"""
    <div style="
        background:#ffffff; border:1px solid #d6ba97; border-radius:18px;
        box-shadow:0 10px 26px rgba(15, 51, 16, 0.06); padding:22px 26px;
    ">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-bottom:6px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:#0f3310;">{ICON_MAP_PIN}</span>
                <div style="font-size:22px; font-weight:800; color:#0f3310;">
                    {html.escape(display_value(row.get("Neighbourhood")))}
                </div>
            </div>
            <span style="
                display:inline-block; padding:5px 12px; border-radius:999px;
                font-size:12px; font-weight:700; {confidence_style}
            ">Confidence: {html.escape(confidence)}</span>
        </div>
        <div style="font-size:14px; color:#0f3310; line-height:1.6; margin:10px 0 14px 0;">
            {html.escape(display_value(row.get("Summary")))}
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:16px; margin-bottom:10px;">
            <div style="flex:1; min-width:200px; margin-bottom:12px;">
                <div style="font-size:11px; color:#0f3310; font-weight:600; margin-bottom:2px;">DOMINANT SEGMENTS</div>
                <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(row.get("Dominant Segments")))}</div>
            </div>
            <div style="flex:1; min-width:200px; margin-bottom:12px;">
                <div style="font-size:11px; color:#0f3310; font-weight:600; margin-bottom:2px;">NOTABLE COMMUNITIES</div>
                <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(row.get("Notable Communities")))}</div>
            </div>
            <div style="flex:1; min-width:200px; margin-bottom:12px;">
                <div style="font-size:11px; color:#0f3310; font-weight:600; margin-bottom:2px;">SPENDING PROFILE</div>
                <div style="font-size:13px; color:#0f3310;">{html.escape(display_value(row.get("Spending Profile")))}</div>
            </div>
            {detail_html}
        </div>
        <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:6px;">QUICK TAGS</div>
        <div style="margin-bottom:12px;">{tags_html if tags_html else '<span style="font-size:12px; color:#0f3310;">No strong tags detected</span>'}</div>
        <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:6px;">SUGGESTED RANGE FOCUS</div>
        <div>{chips_html}</div>
        <div style="font-size:11px; color:#0f3310; margin-top:14px;">
            AI-researched overview — directional only, not verified statistics. Spot-check before using for sourcing decisions.
        </div>
    </div>
    """


def render_trend_card(rank, trend, strength, description, image_path=None, validation=None, search_message=""):
    image_html = """
        <div style="
            width:96px;
            height:96px;
            border-radius:999px;
            background:#d1f694;
            flex-shrink:0;
        "></div>
    """
    image_src = None
    if image_path and str(image_path).startswith(("http://", "https://")):
        image_src = str(image_path)
    else:
        image_src = image_path_to_data_uri(image_path) if image_path else None
    if image_src:
        image_html = f"""
            <img src="{html.escape(image_src, quote=True)}" style="
                width:96px;
                height:96px;
                border-radius:999px;
                object-fit:cover;
                flex-shrink:0;
                box-shadow:0 8px 18px rgba(15, 51, 16, 0.08);
            ">
        """
    strength_style = strength_chip_style(strength)
    validation_html = ""
    if validation:
        validation_html = f"""
                <div style="
                    display:inline-block;
                    padding:6px 14px;
                    border-radius:999px;
                    font-size:14px;
                    font-weight:700;
                    {validation_chip_style(validation)}
                ">{html.escape(display_value(validation))}</div>
        """
    search_html = ""
    if search_message:
        search_html = f"""
            <div style="margin-top:10px; font-size:13px; line-height:1.5; color:#0f3310; background:#f6f0e9; border:1px solid #d6ba97; border-radius:10px; padding:8px 12px;">
                {html.escape(display_value(search_message))}
            </div>
        """
    return f"""
    <div style="
        display:flex;
        gap:14px;
        align-items:flex-start;
        background:#ffffff;
        border:1px solid #d6ba97;
        border-radius:16px;
        padding:14px 16px;
        box-shadow: 0 8px 18px rgba(15, 51, 16, 0.06);
        margin-bottom:14px;
    ">
        <div style="
            width:30px;
            height:30px;
            border-radius:8px;
            background:#0f3310;
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:15px;
            font-weight:800;
            flex-shrink:0;
            margin-top:4px;
        ">{int(rank)}</div>
        {image_html}
        <div style="flex:1; min-width:0;">
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                <div style="font-size:24px; font-weight:800; color:#0f3310;">
                    {html.escape(display_value(trend))}
                </div>
                <div style="
                    display:inline-block;
                    padding:6px 14px;
                    border-radius:999px;
                    font-size:14px;
                    font-weight:700;
                    {strength_style}
                ">{html.escape(display_value(strength))}</div>
                {validation_html}
            </div>
            <div style="margin-top:8px; font-size:14px; line-height:1.55; color:#0f3310;">
                {html.escape(display_value(description))}
            </div>
            {search_html}
        </div>
    </div>
    """


_LEGAL_SUFFIX_RE = re.compile(
    r"\b(ltd|limited|llc|inc|plc|co|company|gmbh|srl|sarl|oy|ab|bv|nv|sa|ag|kft|doo)\b",
    re.I,
)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]+")
RETAIL_CHAIN_NEEDLES = (
    "wolt market",
    "the convenience shop",
    "savemart",
    "welbee",
    "tower supermarket",
    "smart supermarket",
    "interspar",
    "eurospar",
    "arkadia",
    "is-suq tal-belt",
    "is suq tal belt",
    "lidl",
    "aldi",
    "tesco",
    "carrefour",
    "maxima",
    "rimi",
    "prisma",
    "k-market",
    "s-market",
    "mercadona",
    "pingo doce",
    "auchan",
    "rewe",
    "edeka",
)
RETAIL_CHAIN_REGEXES = (
    re.compile(r"\bspar\b", re.I),
    re.compile(r"\bsupermarket\b", re.I),
    re.compile(r"\bmini markets?\b", re.I),
    re.compile(r"\bconvenience shops?\b", re.I),
    re.compile(r"\bgrocers\b", re.I),
    re.compile(r"\bproduce (shops|counters)\b", re.I),
)


def normalize_supplier_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    text = _LEGAL_SUFFIX_RE.sub(" ", text)
    text = _NON_ALNUM_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def producer_identity(name: str) -> str:
    """Stable key so 'KEAN' and 'KEAN / local water' count as one producer."""
    raw = str(name or "")
    raw = re.sub(r"\([^)]*\)", " ", raw)
    raw = raw.split("/")[0]
    return normalize_supplier_name(raw)


def producer_match_candidates(name: str) -> list:
    """Names to try against the WM vendor list, including slash-separated brands."""
    raw = str(name or "").strip()
    parts = [raw]
    for chunk in re.split(r"[/,]", raw):
        chunk = chunk.strip()
        if chunk and chunk not in parts:
            parts.append(chunk)
    keys = []
    seen = set()
    for part in parts:
        key = normalize_supplier_name(re.sub(r"\([^)]*\)", " ", part))
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


# Island-wide / export factory brands. Always excluded from Hyperlocal Range.
NATIONAL_PRODUCER_KEYS = {
    "CYP": {"kean", "charalambides christis", "charalambides", "pittas", "keo"},
    "MLT": {"farsons", "farsons cask", "kinnie"},
    "AZE": {"badamli", "sirab"},
}

# Same physical store, two names CMs search for.
CITY_FILTER_ALIASES = {
    ("CYP", "Paralimni"): ["Paralimni", "Ammochostos"],
    ("CYP", "Ammochostos"): ["Ammochostos", "Paralimni"],
}


def city_filter_values(country: str, city: str):
    if not city or city == "All":
        return None
    return CITY_FILTER_ALIASES.get((str(country or ""), str(city)), [city])


def infer_producer_scale(country: str, name: str, existing: str = "") -> str:
    folded = normalize_supplier_name(name)
    ident = producer_identity(name)
    keys = NATIONAL_PRODUCER_KEYS.get(str(country).strip(), set())
    if ident in keys or any(k == ident or f" {k} " in f" {folded} " for k in keys):
        return "National"
    current = str(existing or "").strip().title()
    if current in {"National", "Hyperlocal"}:
        return current
    return "Hyperlocal"


def is_retail_chain_name(name: str) -> bool:
    raw = str(name or "")
    folded = normalize_supplier_name(raw)
    lowered = raw.lower()
    if any(needle in folded or needle in lowered for needle in RETAIL_CHAIN_NEEDLES):
        return True
    return any(rx.search(raw) or rx.search(folded) for rx in RETAIL_CHAIN_REGEXES)


_SKIP_VENDOR_KEYS = {"and", "the", "ltd", "co", "cyprus", "wolt", "market", "vendor"}


def _vendor_alias_index(vendors_df: pd.DataFrame) -> dict:
    index = {}
    if vendors_df is None or vendors_df.empty or "Vendor" not in vendors_df.columns:
        return index
    work = vendors_df.copy()
    if "Country" not in work.columns:
        work["Country"] = ""
    for _, row in work.iterrows():
        vendor = str(row.get("Vendor", "")).strip()
        if vendor in {"", "N/A", "nan", "None"}:
            continue
        country = str(row.get("Country", "")).strip()
        skus = pd.to_numeric(pd.Series([row.get("SKUs")]), errors="coerce").iloc[0]
        skus = int(skus) if pd.notna(skus) else 0
        key = normalize_supplier_name(vendor)
        if len(key) < 3 or key in _SKIP_VENDOR_KEYS:
            continue
        index.setdefault(country, []).append((key, vendor, skus))
    return index


def _whole_word(needle: str, haystack: str) -> bool:
    if not needle or not haystack:
        return False
    return bool(re.search(rf"(^|\s){re.escape(needle)}(\s|$)", haystack))


def _score_name_against_alias(name: str, alias: str) -> float:
    if not name or not alias:
        return 0.0
    if name == alias:
        return 1.0
    if _whole_word(alias, name) or _whole_word(name, alias):
        return 0.97 if min(len(alias), len(name)) >= 3 else 0.0
    if alias in name or name in alias:
        shorter = alias if len(alias) <= len(name) else name
        if len(shorter) >= 8:
            return 0.96 if alias in name else 0.93
        return SequenceMatcher(None, name, alias).ratio()
    score = SequenceMatcher(None, name, alias).ratio()
    tokens = [token for token in name.split() if len(token) >= 4]
    if len(tokens) >= 2 and all(token in alias for token in tokens):
        score = max(score, 0.9)
    return score


def match_producer_to_vendor(producer_name: str, aliases) -> tuple:
    if not aliases:
        return "", 0.0
    best_vendor = ""
    best_score = 0.0
    best_skus = -1
    for name in producer_match_candidates(producer_name):
        for alias, vendor, skus in aliases:
            score = _score_name_against_alias(name, alias)
            if score > best_score or (abs(score - best_score) < 1e-9 and skus > best_skus):
                best_score = score
                best_vendor = vendor
                best_skus = skus
    if best_score >= 0.86:
        return best_vendor, best_score
    return "", 0.0


def collapse_duplicate_producers(df: pd.DataFrame) -> pd.DataFrame:
    """One row per producer identity; extra catchments go in 'Also ranged in'."""
    if df is None or df.empty or "Producer" not in df.columns:
        return df
    work = df.copy()
    work["_identity"] = work["Producer"].map(producer_identity)
    work = work[work["_identity"] != ""]
    if work.empty:
        return df
    rows = []
    for _, group in work.groupby("_identity", sort=False):
        group = group.copy()
        websites = group["Website / IG"].astype(str) if "Website / IG" in group.columns else pd.Series([""] * len(group), index=group.index)
        ranked = group.assign(_web=websites.where(~websites.isin({"", "N/A", "nan", "None"}), other=""))
        ranked = ranked.sort_values("_web", ascending=False)
        keep = ranked.iloc[0].drop(labels=["_web"], errors="ignore")
        neighbourhoods = []
        if "Neighbourhood" in group.columns:
            neighbourhoods = [
                str(n).strip()
                for n in group["Neighbourhood"].tolist()
                if str(n).strip() not in {"", "N/A", "nan", "None"}
            ]
        unique_nb = list(dict.fromkeys(neighbourhoods))
        primary = str(keep.get("Neighbourhood", "")).strip()
        extras = [n for n in unique_nb if n != primary]
        keep["Also ranged in"] = "; ".join(extras) if extras else "N/A"
        rows.append(keep.drop(labels=["_identity"], errors="ignore"))
    return pd.DataFrame(rows).reset_index(drop=True)


def annotate_producer_listing(producers: pd.DataFrame, vendors: pd.DataFrame) -> pd.DataFrame:
    if producers is None or producers.empty:
        return producers
    out = producers.copy()
    vendor_index = _vendor_alias_index(vendors)
    statuses = []
    matched = []
    kinds = []
    scales = []
    for _, row in out.iterrows():
        name = str(row.get("Producer", "")).strip()
        country = str(row.get("Country", "")).strip()
        aliases = vendor_index.get(country, [])
        if not aliases and "" in vendor_index:
            aliases = vendor_index.get("", [])
        vendor, score = match_producer_to_vendor(name, aliases)
        if is_retail_chain_name(name):
            kinds.append("retail_chain")
            statuses.append("Grocery chain")
            matched.append(vendor if vendor else "N/A")
        elif vendor:
            kinds.append("existing_supplier")
            statuses.append("Already listed")
            matched.append(vendor)
        else:
            kinds.append("new_lead")
            statuses.append("New lead")
            matched.append("N/A")
        scales.append(infer_producer_scale(country, name, str(row.get("Scale", ""))))
        _ = score
    out["Listing kind"] = kinds
    out["Supplier status"] = statuses
    out["Matched WM vendor"] = matched
    out["Scale"] = scales
    return out


# -----------------------
# LOAD DATA (multi-country)
# -----------------------
DATA_DIR = Path("data")
SKIP_FOLDER_NAMES = {"assets", "devcontainer", "node_modules", "__pycache__"}
PRODUCER_FILES = ["producers.csv", "malta_producers.csv"]
CREATOR_FILES = ["creators.csv", "local_market_creators.csv"]
TREND_FILES = ["trends.csv", "local_market_trends.csv"]
SEARCH_FILES = ["search.csv"]
VENDOR_FILES = ["vendors.csv"]
NEIGHBOURHOOD_FILES = [
    "neighbourhoods.csv",
    "neighbourhood_demographics.csv",
    "Malta_neighbourhood_demographics.csv",
]


def _first_existing(folder: Path, names):
    for name in names:
        path = folder / name
        if path.exists():
            return path
    return None


def _read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, keep_default_na=False)
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df.replace({"": "N/A"}).fillna("N/A")


def _ensure_country(df: pd.DataFrame, code: str) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    if "Country" not in out.columns:
        out.insert(0, "Country", code)
    else:
        blank = out["Country"].astype(str).str.strip().isin({"", "N/A", "nan", "None"})
        out.loc[blank, "Country"] = code
    return out


def _concat(frames):
    frames = [f for f in frames if f is not None and not f.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _scatter_tile_map(df, *, map_style="carto-positron", **kwargs):
    """Plotly 5.24+ uses scatter_map; older builds still have scatter_mapbox."""
    if hasattr(px, "scatter_map"):
        fig = px.scatter_map(df, **kwargs)
        fig.update_layout(map_style=map_style)
    else:
        fig = px.scatter_mapbox(df, **kwargs)
        fig.update_layout(mapbox_style=map_style)
    fig.update_layout(
        font=dict(family="Omnes, Nunito, sans-serif", color=WM_GREEN, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=CATEGORY_PIE_COLORS,
    )
    return fig


def _country_folders():
    """Find country packs in data/ (local layout) and at the repo root (GitHub layout)."""
    found = {}
    for root in (DATA_DIR, Path(".")):
        if not root.exists() or not root.is_dir():
            continue
        for path in root.iterdir():
            if not path.is_dir():
                continue
            name = path.name
            if name.startswith((".", "_")) or name.lower() in SKIP_FOLDER_NAMES:
                continue
            if not _first_existing(path, PRODUCER_FILES):
                continue
            # Prefer data/{CODE} over a same-named folder at the repo root.
            if name not in found or root == DATA_DIR:
                found[name] = path
    return [found[code] for code in sorted(found)]


def load_country_registry() -> pd.DataFrame:
    for path in (DATA_DIR / "countries.csv", Path("countries.csv")):
        if path.exists():
            registry = pd.read_csv(path)
            registry["code"] = registry["code"].astype(str).str.strip()
            return registry
    return pd.DataFrame(columns=["code", "name", "latitude", "longitude", "zoom"])


def load_cities_registry() -> pd.DataFrame:
    for path in (DATA_DIR / "cities.csv", Path("cities.csv")):
        if path.exists():
            cities = pd.read_csv(path, keep_default_na=False)
            if "Country" in cities.columns:
                cities["Country"] = cities["Country"].astype(str).str.strip()
            if "City" in cities.columns:
                cities["City"] = cities["City"].astype(str).str.strip()
            return cities
    return pd.DataFrame(columns=["Country", "City", "Latitude", "Longitude", "Zoom", "Store status"])


def _load_folder_pack(folder: Path, code: str):
    pack = {
        "producers": None,
        "creators": None,
        "trends": None,
        "neighbourhoods": None,
        "search": None,
        "vendors": None,
    }
    prod = _first_existing(folder, PRODUCER_FILES)
    if prod:
        pack["producers"] = _ensure_country(_read_csv(prod), code)
    crea = _first_existing(folder, CREATOR_FILES)
    if crea:
        pack["creators"] = _ensure_country(_read_csv(crea), code)
    tren = _first_existing(folder, TREND_FILES)
    if tren:
        pack["trends"] = _ensure_country(_read_csv(tren), code)
    demo = _first_existing(folder, NEIGHBOURHOOD_FILES)
    if demo:
        pack["neighbourhoods"] = _ensure_country(_read_csv(demo), code)
    sear = _first_existing(folder, SEARCH_FILES)
    if sear:
        pack["search"] = _ensure_country(_read_csv(sear), code)
    vend = _first_existing(folder, VENDOR_FILES)
    if vend:
        pack["vendors"] = _ensure_country(_read_csv(vend), code)
    return pack


def _data_fingerprint() -> str:
    """Invalidate cached loads when a country CSV is edited."""
    parts = []
    folders = list(_country_folders())
    if not any(folder.name == "MLT" for folder in folders):
        folders.append(Path("."))
    for folder in folders:
        if not folder.exists():
            continue
        for names in (
            PRODUCER_FILES,
            CREATOR_FILES,
            TREND_FILES,
            NEIGHBOURHOOD_FILES,
            SEARCH_FILES,
            VENDOR_FILES,
        ):
            path = _first_existing(folder, names)
            if path is None:
                continue
            info = path.stat()
            parts.append(f"{path.resolve()}:{info.st_mtime_ns}:{info.st_size}")
    for extra in (
        DATA_DIR / "countries.csv",
        Path("countries.csv"),
        DATA_DIR / "cities.csv",
        Path("cities.csv"),
    ):
        if extra.exists():
            info = extra.stat()
            parts.append(f"{extra.resolve()}:{info.st_mtime_ns}:{info.st_size}")
    return "|".join(parts)


def _attach_search_validation(trends: pd.DataFrame, search: pd.DataFrame) -> pd.DataFrame:
    if trends is None or trends.empty:
        return trends
    statuses, messages, counts = [], [], []
    for _, row in trends.iterrows():
        result = validate_trend_against_search(row, search)
        statuses.append(result["status"])
        messages.append(result["message"])
        counts.append(result["searches"])
    out = trends.copy()
    out["Search Status"] = statuses
    out["Search Message"] = messages
    out["Search Count"] = counts
    return out


@st.cache_data(show_spinner=False)
def load_all_market_data(fingerprint: str = ""):
    _ = fingerprint  # cache key: country CSV paths, sizes, and mtimes
    registry = load_country_registry()
    producers, creators, trends, neighbourhoods, searches, vendors = [], [], [], [], [], []

    folders = _country_folders()
    loaded_codes = set()
    for folder in folders:
        code = folder.name
        pack = _load_folder_pack(folder, code)
        if pack["producers"] is not None:
            producers.append(pack["producers"])
        if pack["creators"] is not None:
            creators.append(pack["creators"])
        if pack["trends"] is not None:
            trends.append(pack["trends"])
        if pack["neighbourhoods"] is not None:
            neighbourhoods.append(pack["neighbourhoods"])
        if pack["search"] is not None:
            searches.append(pack["search"])
        if pack["vendors"] is not None:
            vendors.append(pack["vendors"])
        loaded_codes.add(code)
        if registry.empty or code not in set(registry["code"].astype(str)):
            extra = pd.DataFrame(
                [{"code": code, "name": code, "latitude": "", "longitude": "", "zoom": ""}]
            )
            registry = pd.concat([registry, extra], ignore_index=True)

    # GitHub / older layout: Malta CSVs sit in the project root, not in MLT/.
    if "MLT" not in loaded_codes:
        root = Path(".")
        pack = _load_folder_pack(root, "MLT")
        if pack["producers"] is not None:
            producers.append(pack["producers"])
        if pack["creators"] is not None:
            creators.append(pack["creators"])
        if pack["trends"] is not None:
            trends.append(pack["trends"])
        if pack["neighbourhoods"] is not None:
            neighbourhoods.append(pack["neighbourhoods"])
        if pack["search"] is not None:
            searches.append(pack["search"])
        if pack["vendors"] is not None:
            vendors.append(pack["vendors"])
        if pack["producers"] is not None and (
            registry.empty or "MLT" not in set(registry["code"].astype(str))
        ):
            extra = pd.DataFrame(
                [{"code": "MLT", "name": "Malta", "latitude": 35.94, "longitude": 14.40, "zoom": 9}]
            )
            registry = pd.concat([registry, extra], ignore_index=True)

    trends_out = _concat(trends)
    search_out = _concat(searches)
    vendors_out = _concat(vendors)
    trends_out = _attach_search_validation(trends_out, search_out)
    producers_out = annotate_producer_listing(_concat(producers), vendors_out)
    return (
        registry,
        producers_out,
        _concat(creators),
        trends_out,
        _concat(neighbourhoods),
        search_out,
        vendors_out,
    )


def country_display_name(code: str, registry: pd.DataFrame) -> str:
    if registry.empty or "code" not in registry.columns:
        return str(code)
    match = registry[registry["code"].astype(str) == str(code)]
    if match.empty:
        return str(code)
    name = match.iloc[0].get("name", code)
    return str(name) if str(name).strip() not in {"", "nan"} else str(code)


def map_view_for(df: pd.DataFrame, registry_row=None):
    if registry_row is not None:
        lat = pd.to_numeric(pd.Series([registry_row.get("latitude")]), errors="coerce").iloc[0]
        lon = pd.to_numeric(pd.Series([registry_row.get("longitude")]), errors="coerce").iloc[0]
        zoom = pd.to_numeric(pd.Series([registry_row.get("zoom")]), errors="coerce").iloc[0]
        if pd.notna(lat) and pd.notna(lon):
            return {"lat": float(lat), "lon": float(lon)}, int(zoom) if pd.notna(zoom) else 8

    if df is None or df.empty:
        return {"lat": 50.0, "lon": 15.0}, 4

    lat = pd.to_numeric(df.get("Latitude_num", df.get("Latitude")), errors="coerce")
    lon = pd.to_numeric(df.get("Longitude_num", df.get("Longitude")), errors="coerce")
    valid = lat.notna() & lon.notna()
    if not valid.any():
        return {"lat": 50.0, "lon": 15.0}, 4
    lat_span = float(lat[valid].max() - lat[valid].min())
    zoom = 4 if lat_span > 8 else 6 if lat_span > 2 else 9
    return {"lat": float(lat[valid].mean()), "lon": float(lon[valid].mean())}, zoom


(
    registry_df,
    all_producers_df,
    all_creators_df,
    all_trends_df,
    all_demographics_df,
    all_search_df,
    all_vendors_df,
) = load_all_market_data(_data_fingerprint())
cities_df = load_cities_registry()

if all_producers_df.empty:
    st.error(
        "No producer data found. Add data/MLT/producers.csv, or drop a new country folder "
        "under data/ (see data/HOW_TO_ADD_A_COUNTRY.txt)."
    )
    st.stop()

all_producers_df["Latitude_num"] = pd.to_numeric(all_producers_df.get("Latitude"), errors="coerce")
all_producers_df["Longitude_num"] = pd.to_numeric(all_producers_df.get("Longitude"), errors="coerce")

country_codes = sorted(all_producers_df["Country"].dropna().astype(str).unique().tolist())
country_labels = {code: country_display_name(code, registry_df) for code in country_codes}
country_options = ["All countries"] + [country_labels[c] for c in country_codes]
label_to_code = {v: k for k, v in country_labels.items()}
malta_label = country_labels.get("MLT")
if malta_label in country_options:
    default_country_index = country_options.index(malta_label)
elif len(country_options) > 1:
    default_country_index = 1
else:
    default_country_index = 0

# -----------------------
# SIDEBAR FILTERS
# -----------------------
st.sidebar.markdown(
    clean_html('<div class="wm-hand">Wolt Market</div>'),
    unsafe_allow_html=True,
)
st.sidebar.title("Filters")
selected_country_label = st.sidebar.selectbox("Country", country_options, index=default_country_index)
selected_country_code = None if selected_country_label == "All countries" else label_to_code.get(selected_country_label)

df = all_producers_df.copy()
creators_df = all_creators_df.copy()
trends_df = all_trends_df.copy()
demographics_df = all_demographics_df.copy()
search_df = all_search_df.copy()

if selected_country_code:
    df = df[df["Country"].astype(str) == selected_country_code]
    if not creators_df.empty and "Country" in creators_df.columns:
        creators_df = creators_df[creators_df["Country"].astype(str) == selected_country_code]
    if not trends_df.empty and "Country" in trends_df.columns:
        trends_df = trends_df[trends_df["Country"].astype(str) == selected_country_code]
    if not demographics_df.empty and "Country" in demographics_df.columns:
        demographics_df = demographics_df[demographics_df["Country"].astype(str) == selected_country_code]
    if not search_df.empty and "Country" in search_df.columns:
        search_df = search_df[search_df["Country"].astype(str) == selected_country_code]
    MARKET_NAME = selected_country_label
    registry_row = None
    if not registry_df.empty:
        hit = registry_df[registry_df["code"].astype(str) == selected_country_code]
        if not hit.empty:
            registry_row = hit.iloc[0]
    MAP_CENTER, MAP_ZOOM = map_view_for(df, registry_row)
else:
    MARKET_NAME = "Wolt Market"
    MAP_CENTER, MAP_ZOOM = map_view_for(df)

national_hidden = 0
if "Scale" in df.columns:
    national_hidden = int((df["Scale"].astype(str) == "National").sum())
    df = df[df["Scale"].astype(str) != "National"].copy()

if not creators_df.empty and "Name / Handle" in creators_df.columns:
    creators_df["Profile Pic"] = creators_df["Name / Handle"].apply(resolve_creator_pic)

selected_city = "All"
selected_city_status = ""
selected_city_row = None

def _city_options_for(country_code: str):
    names = []
    meta = {}
    if cities_df is not None and not cities_df.empty and country_code:
        scoped = cities_df[cities_df["Country"].astype(str) == str(country_code)]
        for _, row in scoped.iterrows():
            name = str(row.get("City", "")).strip()
            if name and name.lower() not in {"n/a", "nan", "none"}:
                names.append(name)
                meta[name] = row
    if "City" in df.columns:
        for name in _choice_values(df["City"]):
            if name not in meta:
                names.append(name)
    order = {"Live store": 0, "In range": 1, "Expansion": 2}

    def sort_key(name):
        row = meta.get(name)
        status = str(row.get("Store status", "")) if row is not None else "In range"
        return (order.get(status, 9), name.lower())

    unique = []
    seen = set()
    for name in names:
        if name not in seen:
            unique.append(name)
            seen.add(name)
    unique.sort(key=sort_key)
    return unique, meta

if selected_country_code:
    city_names, city_meta = _city_options_for(selected_country_code)
    if city_names:
        def _city_label(name):
            if name == "All":
                return "All"
            row = city_meta.get(name)
            status = str(row.get("Store status", "")).strip() if row is not None else ""
            if status == "Expansion":
                return f"{name}  ·  no store yet"
            if status == "In range":
                return f"{name}  ·  ranged, no store"
            if status == "Live store":
                return f"{name}  ·  live store"
            return name

        selected_city = st.sidebar.selectbox(
            "City",
            ["All"] + city_names,
            format_func=_city_label,
            key=f"city_{selected_country_code}",
        )
        if selected_city != "All":
            selected_city_row = city_meta.get(selected_city)
            if selected_city_row is not None:
                selected_city_status = str(selected_city_row.get("Store status", "")).strip()
            if selected_city_status == "Expansion":
                st.sidebar.caption("Planning view — no live Wolt Market store in this city yet.")
            elif selected_city_status == "In range":
                st.sidebar.caption("Producers here are ranged from nearby stores; no WM store in this city.")

hide_retail_chains = st.sidebar.checkbox(
    "Hide grocery chains & Wolt stores",
    value=True,
    help="Hides Wolt Market venues, SPAR/EUROSPAR, SaveMart, convenience chains and generic grocery rows so the list is actual producers.",
)
supplier_mode = st.sidebar.selectbox(
    "WM supplier list",
    ["All", "New leads only", "Already listed"],
    help="Match against vendors.csv for this country. Existing suppliers stay visible unless you choose New leads only.",
)
if all_vendors_df is None or all_vendors_df.empty:
    st.sidebar.caption("No vendors.csv for this market yet — supplier matching is off.")
elif selected_country_code:
    country_vendors = all_vendors_df[all_vendors_df["Country"].astype(str) == selected_country_code]
    if country_vendors.empty:
        st.sidebar.caption("No vendor extract for this country yet.")
    else:
        st.sidebar.caption(f"{len(country_vendors)} WM vendors loaded for matching.")

city_scope_df = df.copy()
if "City" in df.columns and selected_city != "All":
    city_vals = city_filter_values(selected_country_code, selected_city)
    city_scope_df = city_scope_df[city_scope_df["City"].astype(str).str.strip().isin(city_vals)]
if hide_retail_chains and "Listing kind" in city_scope_df.columns:
    city_scope_df = city_scope_df[city_scope_df["Listing kind"] != "retail_chain"]
if supplier_mode == "New leads only" and "Listing kind" in city_scope_df.columns:
    city_scope_df = city_scope_df[city_scope_df["Listing kind"] == "new_lead"]
elif supplier_mode == "Already listed" and "Listing kind" in city_scope_df.columns:
    city_scope_df = city_scope_df[city_scope_df["Listing kind"] == "existing_supplier"]

nbhd_names = _choice_values(city_scope_df["Neighbourhood"])
if selected_city != "All" and not demographics_df.empty and "City" in demographics_df.columns:
    demo_city = demographics_df[
        demographics_df["City"].astype(str).str.strip().isin(city_filter_values(selected_country_code, selected_city))
    ]
    for name in _choice_values(demo_city["Neighbourhood"]):
        if name not in nbhd_names:
            nbhd_names.append(name)
    nbhd_names = sorted(nbhd_names)

neighbourhoods = ["All"] + nbhd_names
selected_neighbourhood = st.sidebar.selectbox(
    "Neighbourhood",
    neighbourhoods,
    key=f"nbhd_{selected_country_code or 'all'}_{selected_city}",
)

categories = ["All"] + _choice_values(city_scope_df["Category"])
selected_category = st.sidebar.selectbox(
    "Category",
    categories,
    key=f"cat_{selected_country_code or 'all'}_{selected_city}",
)

search_term = st.sidebar.text_input("Search Producer")
show_only_mapped = st.sidebar.checkbox("Show only rows with coordinates", value=False)

# -----------------------
# FILTER DATA
# -----------------------
filtered_df = df.copy()

if "City" in df.columns and selected_city != "All":
    city_vals = city_filter_values(selected_country_code, selected_city)
    city_match = filtered_df["City"].astype(str).str.strip().isin(city_vals)
    filtered_df = filtered_df[city_match]

if selected_neighbourhood != "All":
    filtered_df = filtered_df[filtered_df["Neighbourhood"] == selected_neighbourhood]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if search_term:
    filtered_df = filtered_df[
        filtered_df["Producer"].astype(str).str.contains(search_term, case=False, na=False)
    ]

if hide_retail_chains and "Listing kind" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Listing kind"] != "retail_chain"]

if supplier_mode == "New leads only" and "Listing kind" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Listing kind"] == "new_lead"]
elif supplier_mode == "Already listed" and "Listing kind" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Listing kind"] == "existing_supplier"]

if show_only_mapped:
    filtered_df = filtered_df.dropna(subset=["Latitude_num", "Longitude_num"])

filtered_df = collapse_duplicate_producers(filtered_df)
filtered_map_df = filtered_df.dropna(subset=["Latitude_num", "Longitude_num"]).copy()

# -----------------------
# MAIN CONTENT
# -----------------------
tab_range, tab_trends, tab_demo = st.tabs(["🏪 Hyperlocal Range", "📈 Local Market Trends", "🧭 Neighbourhood Insights"])

# =========================================================
# TAB 1: HYPERLOCAL RANGE
# =========================================================
with tab_range:
    st.title("Hyperlocal Range")
    st.caption(f"Interactive sourcing dashboard for local producers across {MARKET_NAME}.")

    if selected_city != "All" and selected_city_status in {"Expansion", "In range"}:
        st.markdown(
            clean_html(render_city_planning_card(selected_city, selected_city_status, MARKET_NAME)),
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

    producer_scope = "Across all neighbourhoods"
    if selected_neighbourhood != "All":
        producer_scope = f"In {selected_neighbourhood}"
    elif selected_city != "All":
        producer_scope = f"In {selected_city}"

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(clean_html(top_metric_card("Total Producers", len(filtered_df), producer_scope, icon=ICON_USERS, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#d1f694")), unsafe_allow_html=True)
    with kpi2:
        st.markdown(clean_html(top_metric_card("Neighbourhoods", filtered_df["Neighbourhood"].nunique(), f"Across {MARKET_NAME}" if selected_city == "All" else f"In {selected_city}", icon=ICON_MAP_PIN, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
    with kpi3:
        st.markdown(clean_html(top_metric_card("Categories", filtered_df["Category"].nunique(), "Artisanal categories", icon=ICON_GRID, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
    with kpi4:
        st.markdown(clean_html(top_metric_card("Mapped Rows", len(filtered_map_df), "Have coordinates", icon=ICON_MAP, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)

    st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

    if "Listing kind" in df.columns:
        scope = df.copy()
        if "City" in scope.columns and selected_city != "All":
            scope = scope[scope["City"].astype(str).str.strip().isin(city_filter_values(selected_country_code, selected_city))]
        hidden_chains = int((scope["Listing kind"] == "retail_chain").sum())
        already = int((filtered_df["Listing kind"] == "existing_supplier").sum()) if "Listing kind" in filtered_df.columns else 0
        bits = []
        if hide_retail_chains and hidden_chains:
            bits.append(f"{hidden_chains} grocery-chain / Wolt store rows hidden")
        if already:
            bits.append(f"{already} already on the WM supplier list")
        if bits:
            st.caption(" · ".join(bits) + ". Uncheck the sidebar box or choose Already listed to see them.")
    if national_hidden:
        st.caption(
            f"{national_hidden} island-wide / national brands excluded. "
            "This tab is catchment makers only."
        )

    if filtered_df.empty and selected_city_status == "Expansion":
        st.info(
            f"No local producers listed for {selected_city} yet — that is expected before a first store. "
            "Use the city snapshot below, Neighbourhood Insights, and country-level Local Market Trends to plan ranging."
        )

    if selected_neighbourhood != "All" and not demographics_df.empty:
        demo_match = demographics_df[demographics_df["Neighbourhood"] == selected_neighbourhood]
        if not demo_match.empty:
            st.markdown(
                clean_html(render_neighbourhood_demographic_card(demo_match.iloc[0])),
                unsafe_allow_html=True,
            )
            st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)
    elif (
        selected_city != "All"
        and selected_neighbourhood == "All"
        and selected_city_status == "Expansion"
        and not demographics_df.empty
        and "City" in demographics_df.columns
    ):
        city_demo = demographics_df[
            (demographics_df["City"].astype(str).str.strip() == selected_city)
            & (demographics_df["Neighbourhood"].astype(str).str.strip() == selected_city)
        ]
        if city_demo.empty:
            city_demo = demographics_df[demographics_df["City"].astype(str).str.strip() == selected_city]
        if not city_demo.empty:
            st.markdown(
                clean_html(render_neighbourhood_demographic_card(city_demo.iloc[0])),
                unsafe_allow_html=True,
            )
            st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

    top_left, top_right = st.columns(2, gap="large")
    with top_left:
        st.subheader("Top Categories")
        st.caption("Share of listed local producers in the current filter, by ranging category — not sales.")
        category_counts = filtered_df["Category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]
        if not category_counts.empty:
            fig_donut = px.pie(
                category_counts,
                names="Category",
                values="Count",
                hole=0.48,
                color="Category",
                color_discrete_sequence=CATEGORY_PIE_COLORS,
            )
            fig_donut.update_traces(
                textinfo="none",
                marker=dict(line=dict(color="white", width=2)),
            )
            fig_donut.update_layout(
                height=CHART_HEIGHT,
                margin=dict(r=0, t=20, l=0, b=0),
                font=dict(family="Omnes, Nunito, sans-serif", color=WM_GREEN, size=13),
                paper_bgcolor="rgba(0,0,0,0)",
                legend_title_text="Categories",
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02,
                ),
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No category data.")

    with top_right:
        st.subheader("Top Neighbourhoods")
        st.caption("Towns with the most listed producers in the current filter.")
        neighbourhood_counts = filtered_df["Neighbourhood"].value_counts().reset_index()
        neighbourhood_counts.columns = ["Neighbourhood", "Count"]
        top_neighbourhoods = neighbourhood_counts.head(10).sort_values("Count", ascending=True)
        if not top_neighbourhoods.empty:
            fig_nb = px.bar(
                top_neighbourhoods,
                x="Count",
                y="Neighbourhood",
                orientation="h",
                color="Count",
                color_continuous_scale=PURPLE_SCALE,
                labels={"Count": "Producer Count"},
            )
            fig_nb.update_layout(
                height=CHART_HEIGHT,
                margin=dict(r=0, t=20, l=0, b=0),
                font=dict(family="Omnes, Nunito, sans-serif", color=WM_GREEN, size=13),
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                xaxis_title="Producer count",
                yaxis_title="",
            )
            st.plotly_chart(fig_nb, use_container_width=True)
        else:
            st.info("No neighbourhood data.")

    st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)
    st.subheader(f"{MARKET_NAME} Map")

    map_counts = (
        filtered_map_df
        .groupby(["Neighbourhood", "Latitude_num", "Longitude_num"], as_index=False)
        .agg(Producer_Count=("Producer", "count"))
    )

    map_center, map_zoom = MAP_CENTER, MAP_ZOOM
    if (selected_city != "All" or selected_neighbourhood != "All") and not filtered_map_df.empty:
        map_center, map_zoom = map_view_for(filtered_map_df)
    elif selected_city_row is not None:
        clat = pd.to_numeric(pd.Series([selected_city_row.get("Latitude")]), errors="coerce").iloc[0]
        clon = pd.to_numeric(pd.Series([selected_city_row.get("Longitude")]), errors="coerce").iloc[0]
        cz = pd.to_numeric(pd.Series([selected_city_row.get("Zoom")]), errors="coerce").iloc[0]
        if pd.notna(clat) and pd.notna(clon):
            map_center = {"lat": float(clat), "lon": float(clon)}
            map_zoom = int(cz) if pd.notna(cz) else 12

    if map_counts.empty and selected_city_row is not None:
        clat = pd.to_numeric(pd.Series([selected_city_row.get("Latitude")]), errors="coerce").iloc[0]
        clon = pd.to_numeric(pd.Series([selected_city_row.get("Longitude")]), errors="coerce").iloc[0]
        if pd.notna(clat) and pd.notna(clon):
            map_counts = pd.DataFrame(
                [
                    {
                        "Neighbourhood": selected_city,
                        "Latitude_num": float(clat),
                        "Longitude_num": float(clon),
                        "Producer_Count": 0,
                    }
                ]
            )

    if not map_counts.empty:
        map_counts["bubble_size"] = map_counts["Producer_Count"].clip(lower=1) * 6
        map_counts["label"] = map_counts["Producer_Count"].astype(str)
        fig_map = _scatter_tile_map(
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
            zoom=map_zoom,
            center=map_center,
            height=MAP_HEIGHT,
        )
        fig_map.update_traces(
            textposition="middle center",
            textfont=dict(size=18, color="white"),
            opacity=0.45,
        )
        fig_map.update_layout(
            margin=dict(r=0, t=0, l=0, b=0),
            coloraxis_colorbar=dict(title="Producer Count"),
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True})
    else:
        st.info("No mapped rows available for the current filters.")

    st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)
    st.subheader("Producer Database")

    scenario_options = {
        "No filter / Original order": {
            "score_col": None,
            "desc": "Shows the table as-is, without ranking.",
        },
        "Overall Rank - 60% Reviews + 30% Rating + 10% Social": {
            "score_col": "Overall Rank Score",
            "desc": "Balanced view of popularity, quality, and social presence.",
        },
        "Most Popular - 90% Reviews + 10% Rating": {
            "score_col": "Most Popular Score",
            "desc": "Prioritises popularity using review volume, with rating as support.",
        },
        "Highest Quality - 80% Rating + 20% Reviews": {
            "score_col": "Highest Quality Score",
            "desc": "Prioritises quality, using rating first and review count as backup.",
        },
        "Social Buzz - 70% Social + 20% Reviews + 10% Rating": {
            "score_col": "Social Buzz Score",
            "desc": "Measures online buzz using Instagram/TikTok followers first.",
        },
        "Hidden Gems - High Rating + Low Review Count": {
            "score_col": "Hidden Gems Score",
            "desc": "Finds highly rated stores with fewer reviews.",
        },
    }

    selected_scenario = st.selectbox(
        "Ranking scenario",
        list(scenario_options.keys()),
        index=1,
        key="producer_ranking_scenario",
    )
    st.caption(scenario_options[selected_scenario]["desc"])
    score_col = scenario_options[selected_scenario]["score_col"]

    scored_df = build_producer_scores(filtered_df)
    display_df = scored_df.drop(
        columns=[
            "Latitude",
            "Longitude",
            "Latitude_num",
            "Longitude_num",
            "Photo URL",
            "Photo Source",
        ],
        errors="ignore",
    )

    all_score_cols = [
        "Overall Rank Score",
        "Most Popular Score",
        "Highest Quality Score",
        "Social Buzz Score",
        "Hidden Gems Score",
    ]

    if score_col is not None:
        cols_to_drop = [c for c in all_score_cols if c != score_col and c in display_df.columns]
        display_df = display_df.drop(columns=cols_to_drop, errors="ignore")
        display_df = display_df.sort_values(by=score_col, ascending=False, na_position="last")
        display_df = display_df.rename(columns={score_col: f"{selected_scenario}"})
    else:
        display_df = display_df.drop(
            columns=[c for c in all_score_cols if c in display_df.columns],
            errors="ignore",
        )

    st.markdown("### Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        if "Neighbourhood" in display_df.columns:
            neighbourhood_options = sorted(
                display_df["Neighbourhood"].dropna().astype(str).unique().tolist()
            )
            selected_neighbourhoods = st.multiselect(
                "Neighbourhood",
                options=neighbourhood_options,
                default=[],
                placeholder="All neighbourhoods",
            )
        else:
            selected_neighbourhoods = []

    with filter_col2:
        if "Google Rating" in display_df.columns:
            min_rating = st.slider(
                "Minimum Google Rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.1,
            )
        else:
            min_rating = 0.0

    with filter_col3:
        if "Google Reviews" in display_df.columns:
            min_reviews = st.number_input(
                "Minimum Google Reviews",
                min_value=0,
                value=0,
                step=100,
            )
        else:
            min_reviews = 0

    if selected_neighbourhoods and "Neighbourhood" in display_df.columns:
        display_df = display_df[
            display_df["Neighbourhood"].astype(str).isin(selected_neighbourhoods)
        ]

    # Only apply rating/review cuts when the user raises them. A blank Google
    # field is not a 0-star shop — most of the island range has no rating yet,
    # so a >= 0 comparison was hiding 118 of 121 rows and leaving the three
    # Valletta bakeries that happen to have both a rating and a review count.
    if min_rating > 0 and "Google Rating" in display_df.columns:
        rating_series = pd.to_numeric(display_df["Google Rating"], errors="coerce")
        display_df = display_df[rating_series.fillna(0) >= min_rating]

    if min_reviews > 0 and "Google Reviews" in display_df.columns:
        reviews_series = pd.to_numeric(display_df["Google Reviews"], errors="coerce")
        display_df = display_df[reviews_series.fillna(0) >= min_reviews]

    if score_col is not None and f"{selected_scenario}" in display_df.columns:
        display_df = display_df.sort_values(
            by=f"{selected_scenario}",
            ascending=False,
            na_position="last",
        )

    extra_caption = ""
    if hide_retail_chains:
        extra_caption += " Grocery chains and Wolt stores are hidden."
    if supplier_mode == "New leads only":
        extra_caption += " Showing producers not already on the WM supplier list."
    elif supplier_mode == "Already listed":
        extra_caption += " Showing producers already on the WM supplier list."
    st.caption(
        f"Showing {len(display_df)} of {len(scored_df)} producers "
        f"across {display_df['Neighbourhood'].nunique() if 'Neighbourhood' in display_df.columns else 0} neighbourhoods. "
        "Google rating and review filters stay off at 0, because most producers are not rated yet."
        + extra_caption
    )
    table_df = display_df.copy()
    drop_cols = [c for c in ["Listing kind", "Scale", "_identity", "_web"] if c in table_df.columns]
    if drop_cols:
        table_df = table_df.drop(columns=drop_cols)
    front_cols = [c for c in ["Supplier status", "Matched WM vendor", "Also ranged in"] if c in table_df.columns]
    preferred = [c for c in table_df.columns if c not in set(front_cols)]
    if "Producer" in preferred:
        insert_at = preferred.index("Producer") + 1
        preferred = preferred[:insert_at] + front_cols + preferred[insert_at:]
    preferred = list(dict.fromkeys(preferred))
    st.dataframe(
        table_df.loc[:, preferred].reset_index(drop=True),
        use_container_width=True,
        height=620,
    )

    st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)
    st.subheader("Producer Details")

    producer_names = sorted(
        filtered_df["Producer"].dropna().astype(str).unique().tolist()
    )

    if producer_names:
        selected_producer = st.selectbox(
            "Select Producer",
            producer_names,
            key="producer_select",
        )
        producer_data = filtered_df[
            filtered_df["Producer"] == selected_producer
        ].iloc[0]

        image_source = get_display_image(producer_data)

        st.caption(
            f"{display_value(producer_data['Category'])} · {display_value(producer_data['Neighbourhood'])}"
        )
        listing_kind = str(producer_data.get("Listing kind", "")).strip()
        if listing_kind == "existing_supplier":
            st.caption(
                f"Already listed on Wolt Market as **{display_value(producer_data.get('Matched WM vendor'))}**."
            )
        elif listing_kind == "retail_chain":
            st.caption("Grocery chain / Wolt store — not a sourcing lead.")
        elif listing_kind == "new_lead":
            st.caption("Not matched to the current WM supplier list — treat as a new lead.")

        details_img, details_stats, details_info = st.columns([1, 1, 1], gap="large")
        with details_img:
            if image_source:
                st.image(image_source, use_container_width=True)
            else:
                st.info("No image available")

        with details_stats:
            st.markdown(clean_html(stat_card("Google Rating", producer_data["Google Rating"])), unsafe_allow_html=True)
            st.markdown(clean_html(stat_card("Reviews", producer_data["Google Reviews"])), unsafe_allow_html=True)
            st.markdown(clean_html(stat_card("IG Followers", safe_followers_text(producer_data["Instagram Followers"]))), unsafe_allow_html=True)
            st.markdown(clean_html(stat_card("TikTok Followers", safe_followers_text(producer_data["TikTok Followers"]))), unsafe_allow_html=True)

        with details_info:
            st.markdown("### Key Products / Specialties")
            st.write(display_value(producer_data["Key Products/Specialties"]))
            st.divider()
            st.markdown("### Press Mentions")
            st.write(display_value(producer_data["Press Mentions"]))
            st.divider()
            st.markdown("### Selection Rationale")
            st.write(display_value(producer_data["Selection Rationale"]))
            st.divider()
            st.markdown("### Website / IG")
            if is_valid_link(producer_data["Website / IG"]):
                st.link_button(
                    "Open producer link",
                    producer_data["Website / IG"],
                    use_container_width=True,
                )
            else:
                st.write("-")
    else:
        st.info("No producers available for the current filters.")

# =========================================================
# TAB 2: LOCAL MARKET TRENDS
# =========================================================
with tab_trends:
    st.title("Trend Intelligence")
    st.caption(
        f"Creator signals across {MARKET_NAME}, checked against what customers "
        "actually type in the Wolt Market app (last 90 days)."
    )
    if selected_city != "All" and selected_city_status == "Expansion":
        st.caption(
            f"No live store in {selected_city} yet — these are {MARKET_NAME}-wide trends and search signals "
            "to use when ranging a first dark store there."
        )

    selected_market = MARKET_NAME

    if creators_df.empty:
        st.info("No creator data found for this country. Add creators.csv to the country folder under data/.")
    else:
        creator_count = len(creators_df)
        creators_work = creators_df.copy()

        if "Followers" in creators_work.columns:
            creators_work["Followers_num"] = _clean_numeric(creators_work["Followers"]).fillna(0)
            creators_work = creators_work.sort_values("Followers_num", ascending=False)
        else:
            creators_work["Followers_num"] = 0

        total_followers = int(creators_work["Followers_num"].fillna(0).sum())
        platform_split_df = build_platform_split(creators_work)
        content_focus_df = build_content_focus(creators_work)

        if trends_df.empty:
            st.info(
                f"No trend file for {MARKET_NAME} yet. Add trends.csv to the country folder "
                "under data/ to populate this section."
            )

        if not trends_df.empty:
            if "Rank" not in trends_df.columns:
                trends_df["Rank"] = range(1, len(trends_df) + 1)
            if "Trend" not in trends_df.columns and "Title" in trends_df.columns:
                trends_df["Trend"] = trends_df["Title"]
            if "Description" not in trends_df.columns and "Summary" in trends_df.columns:
                trends_df["Description"] = trends_df["Summary"]
            if "Strength" not in trends_df.columns:
                trends_df["Strength"] = "Medium"
            if "Image" not in trends_df.columns:
                trends_df["Image"] = ""

        trends_to_show = trends_df.head(5).copy() if not trends_df.empty else trends_df.copy()
        trend_validations = []
        for _, row in trends_to_show.iterrows():
            status = str(row.get("Search Status", "")).strip()
            message = str(row.get("Search Message", "")).strip()
            if status in {"", "N/A", "nan", "None"}:
                result = validate_trend_against_search(row, search_df)
                status, message = result["status"], result["message"]
            trend_validations.append({"status": status, "message": message})
        if trend_validations:
            trends_to_show["Search Status"] = [v["status"] for v in trend_validations]
            trends_to_show["Search Message"] = [v["message"] for v in trend_validations]
        validated_n = sum(1 for v in trend_validations if v["status"] == "Validated")

        top_strength = "Strong"
        top_trend_label = "—"
        if not trends_df.empty and "Strength" in trends_df.columns:
            top_strength = strength_score_label(trends_df.iloc[0]["Strength"])
        if not trends_df.empty:
            top_trend_label = display_value(trends_df.iloc[0].get("Trend", ""))
        emerging_count = len(trends_df)
        search_metric_value = (
            f"{validated_n} of {len(trends_to_show)}" if not trends_to_show.empty else "—"
        )

        # ---- 1) Top Trend Strength + Emerging Trends + Search-validated ----
        strength_col1, strength_col2, strength_col3 = st.columns(3)
        with strength_col1:
            st.markdown(clean_html(top_metric_card("Top Trend Strength", top_strength, top_trend_label, icon=ICON_TRENDING_UP, icon_bg="#d1f694", icon_color="#0f3310", value_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
        with strength_col2:
            st.markdown(clean_html(top_metric_card("Emerging Trends", emerging_count, f"Key {MARKET_NAME} themes identified", icon=ICON_LIGHTBULB, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
        with strength_col3:
            st.markdown(clean_html(top_metric_card("Search-validated", search_metric_value, "Creator trends with 200+ matching app searches", icon=ICON_SEARCH, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 2) Top 5 Trends (full width, one card per row) ----
        st.markdown(f"### Top 5 {MARKET_NAME} Trends")
        st.caption(
            "The first chip is the creator/press read (Strong, Medium-strong, Medium). "
            "The second chip is in-venue app search: Validated (200+ matching searches), "
            "Weak signal (30–199), or Not in search."
        )
        for i, (_, row) in enumerate(trends_to_show.iterrows()):
            rank_raw = pd.to_numeric(row.get("Rank", 0), errors="coerce")
            rank = int(rank_raw) if pd.notna(rank_raw) else 0
            trend = display_value(row.get("Trend", ""))
            strength = strength_score_label(row.get("Strength", ""))
            description = display_value(row.get("Description", ""))
            image_path = resolve_trend_image(row.get("Image", ""), trend_row=row)
            validation = trend_validations[i] if i < len(trend_validations) else {}

            st.markdown(
                clean_html(
                    render_trend_card(
                        rank=rank,
                        trend=trend,
                        strength=strength,
                        description=description,
                        image_path=image_path,
                        validation=validation.get("status", ""),
                        search_message=validation.get("message", ""),
                    )
                ),
                unsafe_allow_html=True,
            )

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 3) Total Creators + Total Followers (full width) ----
        creator_col1, creator_col2 = st.columns(2)
        with creator_col1:
            st.markdown(clean_html(top_metric_card("Total Creators", creator_count, f"Tracked {MARKET_NAME} food creators", icon=ICON_USERS, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
        with creator_col2:
            st.markdown(clean_html(top_metric_card("Total Followers", f"{total_followers:,}", "Combined audience", icon=ICON_USER_GROUP, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#d1f694")), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 4) Top Creators table (full width) ----
        st.markdown(f"### Top Creators – {selected_market}  \n**{creator_count} creators**")

        creators_table_df = creators_work.copy()
        cols = [
            c for c in [
                "Profile Pic",
                "Name / Handle",
                "Platform",
                "Followers_num",
                "Content Focus",
                "Key Trend Signals",
                "Example Link",
            ]
            if c in creators_table_df.columns
        ]
        creators_table_df = creators_table_df[cols].copy()
        if "Followers_num" in creators_table_df.columns:
            creators_table_df = creators_table_df.rename(columns={"Followers_num": "Followers"})
            creators_table_df["Followers"] = creators_table_df["Followers"].map(
                lambda x: f"{int(x):,}" if pd.notna(x) else "-"
            )

        st.markdown(clean_html(render_creator_table_html(creators_table_df)), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 5) Platform Split + Content Focus charts (full width) ----
        c_left, c_right = st.columns([1, 1.35], gap="large")
        with c_left:
            st.subheader("Platform Split")
            if not platform_split_df.empty:
                fig_platform = px.pie(
                    platform_split_df,
                    names="Platform",
                    values="Count",
                    hole=0.62,
                    color="Platform",
                    color_discrete_sequence=["#0f3310", "#a1ce47", "#d6ba97"],
                )
                fig_platform.update_traces(
                    textinfo="none",
                    marker=dict(line=dict(color="white", width=2)),
                )
                fig_platform.update_layout(
                    height=300,
                    margin=dict(r=0, t=20, l=0, b=0),
                    font=dict(family="Omnes, Nunito, sans-serif", color=WM_GREEN, size=13),
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=True,
                    legend_title_text="",
                )
                st.plotly_chart(fig_platform, use_container_width=True)
            else:
                st.info("No platform data.")

        with c_right:
            st.subheader("Key Content Topics")
            if not content_focus_df.empty:
                fig_focus = px.bar(
                    content_focus_df,
                    x="Count",
                    y="Bucket",
                    orientation="h",
                    color="Count",
                    color_continuous_scale=PURPLE_SCALE,
                    labels={"Count": "Number of Creators"},
                )
                fig_focus.update_layout(
                    height=300,
                    margin=dict(r=0, t=20, l=0, b=0),
                    font=dict(family="Omnes, Nunito, sans-serif", color=WM_GREEN, size=13),
                    paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    xaxis_title="Number of Creators",
                    yaxis_title="",
                )
                st.plotly_chart(fig_focus, use_container_width=True)
            else:
                st.info("No content focus data.")

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 6) Match candidate catalogue to trends (AI hand-off) ----
        st.markdown(
            clean_html(render_catalogue_header_and_steps(trends_to_show)),
            unsafe_allow_html=True,
        )

        trend_prompt = build_trend_matching_prompt(trends_to_show)
        st.markdown(
            """
            <style>
                div[data-testid="stCode"], div[data-testid="stCodeBlock"] {
                    background-color: #ffffff !important;
                    border: 1px solid #d6ba97 !important;
                    border-top: none !important;
                    border-radius: 0 0 16px 16px !important;
                    margin-top: -14px !important;
                }
                div[data-testid="stCode"] pre, div[data-testid="stCodeBlock"] pre {
                    background-color: transparent !important;
                    font-size: 12px !important;
                    line-height: 1.2 !important;
                }
                div[data-testid="stCode"] code, div[data-testid="stCodeBlock"] code {
                    color: #0f3310 !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.code(trend_prompt, language=None)

        st.markdown(f"<div style='height:{16}px;'></div>", unsafe_allow_html=True)

        st.markdown(
            clean_html(render_catalogue_footer()),
            unsafe_allow_html=True,
        )

# =========================================================
# TAB 3: NEIGHBOURHOOD INSIGHTS
# =========================================================
with tab_demo:
    st.title("Neighbourhood Insights")
    st.caption("Who lives where — turning local demographics into range and stocking decisions.")
    if selected_city != "All" and selected_city_status == "Expansion":
        st.caption(
            f"Planning a first store in {selected_city}: this tab is the demographic snapshot. "
            f"Local Market Trends still uses {MARKET_NAME}-wide creator and search signals."
        )

    if demographics_df.empty:
        st.info(
            "No demographic data found for this country. Add neighbourhoods.csv to the "
            "matching folder under data/ to unlock this tab."
        )
    else:
        demo_work = demographics_df.copy()
        if selected_city != "All" and "City" in demo_work.columns:
            demo_work = demo_work[
                demo_work["City"].astype(str).str.strip().isin(city_filter_values(selected_country_code, selected_city))
            ]
        demo_work["Spending Bucket"] = demo_work["Spending Profile"].apply(spending_bucket)
        demo_work["Tags"] = demo_work.apply(get_neighbourhood_tags, axis=1)

        # ---- 1) KPI row ----
        halal_count = demo_work["Tags"].apply(lambda t: "Halal" in t).sum()
        vegan_count = demo_work["Tags"].apply(lambda t: "Vegan / Plant-based" in t).sum()
        premium_count = demo_work["Tags"].apply(lambda t: "Premium" in t).sum()

        demo_kpi1, demo_kpi2, demo_kpi3, demo_kpi4 = st.columns(4)
        with demo_kpi1:
            st.markdown(clean_html(top_metric_card("Neighbourhoods Profiled", len(demo_work), "AI-researched overviews", icon=ICON_MAP_PIN, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
        with demo_kpi2:
            st.markdown(clean_html(top_metric_card("Halal Demand Areas", int(halal_count), "Flagged for halal range", icon=ICON_USERS, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)
        with demo_kpi3:
            st.markdown(clean_html(top_metric_card("Vegan / Plant-based Areas", int(vegan_count), "Flagged for plant-based range", icon=ICON_GRID, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#d1f694")), unsafe_allow_html=True)
        with demo_kpi4:
            st.markdown(clean_html(top_metric_card("Premium-Tier Areas", int(premium_count), "Flagged for premium range", icon=ICON_TRENDING_UP, icon_bg="#d1f694", icon_color="#0f3310", card_bg="#ffffff")), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 2) Detail card for a selected neighbourhood ----
        st.subheader("Neighbourhood Deep Dive")
        if demo_work.empty:
            label = selected_city if selected_city != "All" else MARKET_NAME
            st.info(
                f"No neighbourhood profiles for {label} yet. "
                "Add a row in neighbourhoods.csv with City set to this city."
            )
        else:
            selected_demo_neighbourhood = st.selectbox(
                "Select a neighbourhood",
                sorted(demo_work["Neighbourhood"].tolist()),
                key=f"demo_detail_select_{selected_country_code}_{selected_city}",
            )
            detail_row = demo_work[demo_work["Neighbourhood"] == selected_demo_neighbourhood].iloc[0]
            st.markdown(clean_html(render_neighbourhood_full_card(detail_row)), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 3) Spending Profile Map, full width ----
        st.subheader("Spending Profile Map")
        coords = (
            df.dropna(subset=["Latitude_num", "Longitude_num"])
            .groupby("Neighbourhood", as_index=False)[["Latitude_num", "Longitude_num"]]
            .mean()
        )
        demo_map = demo_work.merge(coords, on="Neighbourhood", how="inner")
        if selected_city_row is not None:
            clat = pd.to_numeric(pd.Series([selected_city_row.get("Latitude")]), errors="coerce").iloc[0]
            clon = pd.to_numeric(pd.Series([selected_city_row.get("Longitude")]), errors="coerce").iloc[0]
            if pd.notna(clat) and pd.notna(clon):
                missing = demo_work.loc[
                    ~demo_work["Neighbourhood"].isin(demo_map["Neighbourhood"]),
                    ["Neighbourhood", "Dominant Segments", "Notable Communities", "Spending Bucket"],
                ].copy()
                if not missing.empty:
                    missing["Latitude_num"] = float(clat)
                    missing["Longitude_num"] = float(clon)
                    demo_map = pd.concat([demo_map, missing], ignore_index=True)

        demo_map_center, demo_map_zoom = MAP_CENTER, MAP_ZOOM
        if selected_city_row is not None:
            clat = pd.to_numeric(pd.Series([selected_city_row.get("Latitude")]), errors="coerce").iloc[0]
            clon = pd.to_numeric(pd.Series([selected_city_row.get("Longitude")]), errors="coerce").iloc[0]
            cz = pd.to_numeric(pd.Series([selected_city_row.get("Zoom")]), errors="coerce").iloc[0]
            if pd.notna(clat) and pd.notna(clon):
                demo_map_center = {"lat": float(clat), "lon": float(clon)}
                demo_map_zoom = int(cz) if pd.notna(cz) else MAP_ZOOM
        elif not demo_map.empty:
            demo_map_center, demo_map_zoom = map_view_for(demo_map)

        if demo_map.empty:
            st.info("No matching coordinates found for these neighbourhoods yet.")
        else:
            fig_demo_map = _scatter_tile_map(
                demo_map,
                lat="Latitude_num",
                lon="Longitude_num",
                color="Spending Bucket",
                color_discrete_map=SPENDING_BUCKET_COLORS,
                hover_name="Neighbourhood",
                hover_data={
                    "Dominant Segments": True,
                    "Notable Communities": True,
                    "Latitude_num": False,
                    "Longitude_num": False,
                    "Spending Bucket": True,
                },
                zoom=demo_map_zoom,
                center=demo_map_center,
                height=MAP_HEIGHT,
            )
            fig_demo_map.update_traces(marker=dict(size=16))
            fig_demo_map.update_layout(
                margin=dict(r=0, t=0, l=0, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_demo_map, use_container_width=True, config={"scrollZoom": True})
            unmatched = len(demo_work) - len(demo_map)
            if unmatched > 0:
                st.caption(f"{unmatched} neighbourhood(s) have no producer coordinates yet, so aren't shown on the map.")

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 4) Finder tool + Areas by Spending Tier, side by side ----
        finder_col, mix_col = st.columns(2, gap="large")

        with finder_col:
            st.subheader("Find Areas By Need")
            st.caption("Pick a need and instantly see which neighbourhoods are flagged for it — useful when deciding where to push a new range.")
            tag_options = [t[0] for t in DEMOGRAPHIC_TAG_RULES]
            selected_tag = st.selectbox("Show neighbourhoods flagged for:", tag_options, key="demo_tag_filter")
            matching = demo_work[demo_work["Tags"].apply(lambda t: selected_tag in t)]

            if matching.empty:
                st.info(f"No neighbourhoods currently flagged for '{selected_tag}'.")
            else:
                chips = "".join(
                    f"""<span style="
                        display:inline-block; background:#d1f694; color:#0f3310; border:1px solid #d6ba97;
                        font-size:13px; font-weight:700; padding:7px 14px; border-radius:999px; margin:0 8px 8px 0;
                    ">{html.escape(n)}</span>"""
                    for n in matching["Neighbourhood"].tolist()
                )
                st.markdown(
                    clean_html(f"""
                    <div style="background:#ffffff; border:1px solid #d6ba97; border-radius:16px; padding:16px 20px; box-shadow:0 8px 20px rgba(15, 51, 16, 0.06);">
                        <div style="font-size:12px; color:#0f3310; font-weight:600; margin-bottom:10px;">{len(matching)} MATCHING AREAS</div>
                        {chips}
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

        with mix_col:
            st.subheader("Areas by Spending Tier")
            if demo_work.empty:
                st.info("No spending mix to show for this city yet.")
            else:
                bucket_counts = demo_work["Spending Bucket"].value_counts().reset_index()
                bucket_counts.columns = ["Spending Bucket", "Count"]
                fig_bucket = px.pie(
                    bucket_counts,
                    names="Spending Bucket",
                    values="Count",
                    hole=0.55,
                    color="Spending Bucket",
                    color_discrete_map=SPENDING_BUCKET_COLORS,
                )
                fig_bucket.update_traces(textinfo="none", marker=dict(line=dict(color="white", width=2)))
                fig_bucket.update_layout(
                    height=320,
                    margin=dict(r=0, t=20, l=0, b=0),
                    font=dict(family="Omnes, Nunito, sans-serif", color=WM_GREEN, size=13),
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                )
                st.plotly_chart(fig_bucket, use_container_width=True)
                st.markdown(clean_html(render_spend_bracket_legend()), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 5) Full comparison table ----
        st.subheader("All Neighbourhoods — Comparison Table")
        st.caption("Sort or search any column below — useful for cross-checking multiple areas at once before a range decision.")
        if demo_work.empty:
            st.info("No neighbourhood rows to compare for this city yet.")
        else:
            table_cols = [
                "Neighbourhood", "Dominant Segments", "Notable Communities", "Spending Profile",
                "Dietary Considerations", "Product Recommendations", "Confidence",
            ]
            st.dataframe(
                demo_work[table_cols],
                use_container_width=True,
                height=420,
            )
