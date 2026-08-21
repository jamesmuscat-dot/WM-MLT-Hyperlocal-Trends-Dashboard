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

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Hyperlocal & Trend Range Analytics",
    layout="wide",
)

# -----------------------
# GLOBAL STYLES
# -----------------------
st.markdown(
    """
    <style>
        /* Keep the header/toolbar (Share, star, edit, GitHub, sidebar
           collapse arrow) visible — just hide the menu/footer clutter */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* Enough top padding for content to clear the fixed header,
           so the tab bar doesn't render underneath it */
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
CATEGORY_PIE_COLORS = [
    "#6F5CFF",
    "#4B3AD5",
    "#2F6BFF",
    "#F4C84E",
    "#48B26B",
    "#FF8A80",
    "#A06CD5",
    "#2E86C1",
    "#F78FB3",
    "#7F8C8D",
]
PURPLE_SCALE = ["#D9D0FF", "#6F5CFF"]

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


def top_metric_card(label, value, subtitle, icon=None, icon_bg="#EEF0FF", icon_color="#6F5CFF", value_color="#2f3240", card_bg="#ffffff"):
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
        box-shadow: 0 8px 20px rgba(17, 24, 39, 0.06);
        padding: 16px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        height: 116px;
        overflow: hidden;
    ">
        {icon_html}
        <div style="min-width: 0;">
            <div style="font-size: 13px; color: #6b7280; margin-bottom: 6px; font-weight: 600;">
                {esc(label)}
            </div>
            <div style="font-size: 28px; line-height: 1.1; font-weight: 700; color: {value_color};">
                {esc(value)}
            </div>
            <div style="font-size: 12px; color: #9096a3; margin-top: 6px;">
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
        box-shadow: 0 8px 18px rgba(17, 24, 39, 0.06);
    ">
        <div style="font-size: 12px; color: #666; margin-bottom: 6px;">{esc(label)}</div>
        <div style="font-size: 22px; font-weight: 700; line-height: 1;">{esc(value)}</div>
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


def resolve_trend_image(image_value):
    if not image_value:
        return None
    text = str(image_value).strip()
    if text in {"", "N/A", "nan", "None"}:
        return None
    p1 = Path(text)
    if p1.exists():
        return str(p1)
    p2 = TREND_IMAGE_DIR / text
    if p2.exists():
        return str(p2)
    return None


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
                f'box-shadow:0 3px 8px rgba(17,24,39,0.12);">'
            )
        else:
            icons_html.append(f'<span style="font-size:13px; color:#4b5563;">{html.escape(name)}</span>')

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
        return "background:#e6f4ea;color:#2e7d32;"
    if s == "medium":
        return "background:#fff7e6;color:#f59e0b;"
    return "background:#edf2ff;color:#475569;"


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
                    box-shadow:0 6px 14px rgba(17,24,39,0.12);
                ">
            """
        else:
            pic_html = """
                <div style="
                    width:56px;
                    height:56px;
                    border-radius:999px;
                    background:#e9ecf7;
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
                f'style="color:#6F5CFF; font-weight:600; text-decoration:none;">View profile ↗</a>'
            )
        else:
            example_link_html = html.escape(example_link_raw)
        rows.append(
            f"""
            <tr style="border-bottom:1px solid #e7eaf3;">
                <td style="padding:14px 12px; width:84px; vertical-align:middle;">{pic_html}</td>
                <td style="padding:14px 12px; min-width:240px; vertical-align:middle;">
                    <div style="font-weight:700; color:#2f3240; line-height:1.2;">{html.escape(name_part)}</div>
                    <div style="font-size:13px; color:#6b7280; margin-top:3px;">{html.escape(handle_part)}</div>
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
        border:1px solid #e7eaf3;
        border-radius:16px;
        overflow:hidden;
        box-shadow:0 8px 18px rgba(17,24,39,0.05);
    ">
        <div style="max-height:430px; overflow:auto;">
            <table style="
                width:100%;
                border-collapse:collapse;
                table-layout:fixed;
            ">
                <thead>
                    <tr style="
                        background:#fafbfe;
                        color:#8a8f9c;
                        font-size:14px;
                        font-weight:700;
                        border-bottom:1px solid #e7eaf3;
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
        lines.append(f"{rank}. {trend} (Strength: {strength}) — {desc}")

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
        "min-width:44px; border-radius:999px; background:#6F5CFF; color:white; flex-shrink:0;"
    )

    return f"""
    <div>
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="font-size:28px; font-weight:800; color:#2f3240;">Match Your Catalogue to These Trends</div>
            <div style="color:#9096a3;">{ICON_LINK}</div>
        </div>
        <div style="font-size:14px; color:#6b7280; margin-top:4px; margin-bottom:16px;">
            Use AI to match your candidate products to the latest food &amp; drink trends and get a ranked shortlist.
        </div>

        <div style="
            background:#ffffff; border:1px solid #ECEEF3; border-radius:16px;
            box-shadow:0 8px 20px rgba(17,24,39,0.05); padding:18px 22px; margin-bottom:16px;
            display:flex; align-items:center; justify-content:space-between; gap:10px;
        ">
            <div style="display:flex; align-items:center; justify-content:center; gap:14px; flex:1; min-width:0;">
                <div style="{step_icon_wrap}">{ICON_FILE_TEXT}</div>
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#2f3240; font-size:14px;">1. Copy the prompt</div>
                    <div style="font-size:12px; color:#8a8f9c; margin-top:2px;">We've prepared a detailed prompt with the latest trend insights.</div>
                </div>
            </div>
            <div style="color:#c3c7d1; font-size:20px; padding:0 6px;">→</div>
            <div style="display:flex; align-items:center; justify-content:center; gap:14px; flex:1; min-width:0;">
                <div style="{step_icon_wrap}">{ICON_CLIPBOARD_COPY}</div>
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#2f3240; font-size:14px;">2. Paste into AI</div>
                    <div style="font-size:12px; color:#8a8f9c; margin-top:2px;">Open Claude or ChatGPT and paste the prompt.</div>
                </div>
            </div>
            <div style="color:#c3c7d1; font-size:20px; padding:0 6px;">→</div>
            <div style="display:flex; align-items:center; justify-content:center; gap:14px; flex:1; min-width:0;">
                <div style="{step_icon_wrap}">{ICON_CLOUD_UPLOAD}</div>
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#2f3240; font-size:14px;">3. Upload your catalogue</div>
                    <div style="font-size:12px; color:#8a8f9c; margin-top:2px;">Upload your candidate catalogue (CSV or Excel) and get results.</div>
                </div>
            </div>
        </div>

        <div style="
            background:#FFF7E0; border:1px solid #F5E6B8; border-bottom:none;
            border-radius:16px 16px 0 0; padding:14px 20px;
            display:flex; align-items:center; gap:8px; font-weight:700; color:#9A7B1F; font-size:17px;
        ">
            <span style="color:#F5A623;">{ICON_SPARKLES}</span>
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
                    background:#f0f1f5; display:flex; align-items:center; justify-content:center;
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
        <div style="background:#F5F3FF; border:1px solid #E2DBFF; border-radius:16px; padding:16px 20px; text-align:center; margin-bottom:14px;">
            <div style="font-weight:700; color:#6F5CFF; font-size:15px;">Ready to get your ranked shortlist?</div>
            <div style="font-size:13px; color:#6b7280; margin-top:2px;">Choose your preferred AI assistant to continue.</div>
        </div>

        <div style="display:flex; gap:14px;">
            <a href="https://claude.ai/new" target="_blank" rel="noopener noreferrer" style="
                flex:1; display:flex; align-items:center; gap:12px; text-decoration:none;
                background:#ffffff; border:1px solid #ECEEF3; border-radius:14px; padding:14px 16px;
                box-shadow:0 6px 16px rgba(17,24,39,0.05);
            ">
                {claude_icon_html}
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#2f3240; font-size:14px;">Open in Claude</div>
                    <div style="font-size:12px; color:#8a8f9c; margin-top:2px;">Paste the prompt and upload your catalogue</div>
                </div>
            </a>
            <a href="https://chat.openai.com/" target="_blank" rel="noopener noreferrer" style="
                flex:1; display:flex; align-items:center; gap:12px; text-decoration:none;
                background:#ffffff; border:1px solid #ECEEF3; border-radius:14px; padding:14px 16px;
                box-shadow:0 6px 16px rgba(17,24,39,0.05);
            ">
                {gpt_icon_html}
                <div style="min-width:0;">
                    <div style="font-weight:700; color:#2f3240; font-size:14px;">Open in ChatGPT</div>
                    <div style="font-size:12px; color:#8a8f9c; margin-top:2px;">Paste the prompt and upload your catalogue</div>
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
                display:inline-block; background:#EDEBFF; color:#6F5CFF;
                font-size:12px; font-weight:600; padding:5px 12px;
                border-radius:999px; margin:0 6px 6px 0;
            ">{html.escape(c)}</span>"""
            for c in chips
        )

    return f"""
    <div style="
        background:#ffffff; border:1px solid #ECEEF3; border-radius:16px;
        box-shadow:0 8px 20px rgba(17,24,39,0.05); padding:18px 22px; margin-bottom:8px;
    ">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <span style="color:#6F5CFF;">{ICON_MAP_PIN}</span>
            <div style="font-size:18px; font-weight:800; color:#2f3240;">
                {html.escape(display_value(row.get("Neighbourhood")))} — Who lives here
            </div>
        </div>
        <div style="font-size:14px; color:#4b5563; line-height:1.6; margin-bottom:12px;">
            {html.escape(display_value(row.get("Summary")))}
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:16px; margin-bottom:12px;">
            <div style="flex:1; min-width:180px;">
                <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:2px;">DOMINANT SEGMENTS</div>
                <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(row.get("Dominant Segments")))}</div>
            </div>
            <div style="flex:1; min-width:180px;">
                <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:2px;">NOTABLE COMMUNITIES</div>
                <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(row.get("Notable Communities")))}</div>
            </div>
            <div style="flex:1; min-width:180px;">
                <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:2px;">SPENDING PROFILE</div>
                <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(row.get("Spending Profile")))}</div>
            </div>
        </div>
        <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:6px;">SUGGESTED RANGE FOCUS</div>
        <div>{chips_html}</div>
        <div style="font-size:11px; color:#b3b8c2; margin-top:12px;">
            AI-researched overview — directional only, not verified statistics. Spot-check before using for sourcing decisions.
        </div>
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
    "Ultra-premium": "#4B3AD5",
    "Premium": "#6F5CFF",
    "Mixed": "#A99BFF",
    "Mid-range": "#C9BFFF",
    "Budget": "#E6E1FF",
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
        <tr style="border-bottom:1px solid #ECEEF3;">
            <td style="padding:8px 6px;">
                <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{SPENDING_BUCKET_COLORS[tier]}; margin-right:8px;"></span>
                <span style="font-size:13px; font-weight:600; color:#2f3240;">{html.escape(tier)}</span>
            </td>
            <td style="padding:8px 6px; font-size:13px; color:#4b5563;">{html.escape(bracket["weekly"])}</td>
            <td style="padding:8px 6px; font-size:13px; color:#4b5563;">{html.escape(bracket["basket"])}</td>
        </tr>
        """
        for tier, bracket in SPENDING_BUCKET_BRACKETS.items()
    )
    return f"""
    <div>
        <table style="width:100%; border-collapse:collapse; margin-bottom:8px;">
            <thead>
                <tr style="border-bottom:1px solid #ECEEF3;">
                    <th style="text-align:left; padding:6px; font-size:11px; color:#9096a3; font-weight:600;">TIER</th>
                    <th style="text-align:left; padding:6px; font-size:11px; color:#9096a3; font-weight:600;">WEEKLY FOOD SPEND</th>
                    <th style="text-align:left; padding:6px; font-size:11px; color:#9096a3; font-weight:600;">BASKET VALUE</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div style="font-size:11px; color:#b3b8c2;">
            Illustrative brackets, not measured — placeholders pending real average order value (AOV) data.
        </div>
    </div>
    """


CONFIDENCE_BADGE_STYLE = {
    "High": "background:#E6F7EC; color:#2E9E4F;",
    "Medium-High": "background:#E5F0FF; color:#2F6BFF;",
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
                display:inline-block; background:#EDEBFF; color:#6F5CFF;
                font-size:12px; font-weight:600; padding:5px 12px;
                border-radius:999px; margin:0 6px 6px 0;
            ">{html.escape(c)}</span>"""
            for c in chips
        )

    tags = get_neighbourhood_tags(row)
    tags_html = "".join(
        f"""<span style="
            display:inline-block; background:#F5F3FF; color:#6F5CFF;
            font-size:11px; font-weight:700; padding:4px 10px;
            border-radius:999px; margin:0 6px 6px 0; border:1px solid #E2DBFF;
        ">{html.escape(t)}</span>"""
        for t in tags
    )

    confidence = display_value(row.get("Confidence"))
    confidence_style = CONFIDENCE_BADGE_STYLE.get(confidence, "background:#EEF0FF; color:#6F5CFF;")

    detail_fields = [
        ("AGE / LIFE-STAGE SKEW", row.get("Age Life Stage Skew")),
        ("STUDENT / UNIVERSITY PROXIMITY", row.get("Student University Proximity")),
        ("DAY / NIGHT PATTERN", row.get("Day Night Pattern")),
        ("DIETARY CONSIDERATIONS", row.get("Dietary Considerations")),
    ]
    detail_html = "".join(
        f"""
        <div style="flex:1; min-width:200px; margin-bottom:12px;">
            <div style="font-size:11px; color:#9096a3; font-weight:600; margin-bottom:2px;">{label}</div>
            <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(value))}</div>
        </div>
        """
        for label, value in detail_fields
    )

    return f"""
    <div style="
        background:#ffffff; border:1px solid #ECEEF3; border-radius:18px;
        box-shadow:0 10px 26px rgba(17,24,39,0.06); padding:22px 26px;
    ">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-bottom:6px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:#6F5CFF;">{ICON_MAP_PIN}</span>
                <div style="font-size:22px; font-weight:800; color:#2f3240;">
                    {html.escape(display_value(row.get("Neighbourhood")))}
                </div>
            </div>
            <span style="
                display:inline-block; padding:5px 12px; border-radius:999px;
                font-size:12px; font-weight:700; {confidence_style}
            ">Confidence: {html.escape(confidence)}</span>
        </div>
        <div style="font-size:14px; color:#4b5563; line-height:1.6; margin:10px 0 14px 0;">
            {html.escape(display_value(row.get("Summary")))}
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:16px; margin-bottom:10px;">
            <div style="flex:1; min-width:200px; margin-bottom:12px;">
                <div style="font-size:11px; color:#9096a3; font-weight:600; margin-bottom:2px;">DOMINANT SEGMENTS</div>
                <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(row.get("Dominant Segments")))}</div>
            </div>
            <div style="flex:1; min-width:200px; margin-bottom:12px;">
                <div style="font-size:11px; color:#9096a3; font-weight:600; margin-bottom:2px;">NOTABLE COMMUNITIES</div>
                <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(row.get("Notable Communities")))}</div>
            </div>
            <div style="flex:1; min-width:200px; margin-bottom:12px;">
                <div style="font-size:11px; color:#9096a3; font-weight:600; margin-bottom:2px;">SPENDING PROFILE</div>
                <div style="font-size:13px; color:#2f3240;">{html.escape(display_value(row.get("Spending Profile")))}</div>
            </div>
            {detail_html}
        </div>
        <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:6px;">QUICK TAGS</div>
        <div style="margin-bottom:12px;">{tags_html if tags_html else '<span style="font-size:12px; color:#b3b8c2;">No strong tags detected</span>'}</div>
        <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:6px;">SUGGESTED RANGE FOCUS</div>
        <div>{chips_html}</div>
        <div style="font-size:11px; color:#b3b8c2; margin-top:14px;">
            AI-researched overview — directional only, not verified statistics. Spot-check before using for sourcing decisions.
        </div>
    </div>
    """


def render_trend_card(rank, trend, strength, description, image_path=None):
    image_html = """
        <div style="
            width:96px;
            height:96px;
            border-radius:999px;
            background:#e9ecf7;
            flex-shrink:0;
        "></div>
    """
    image_uri = image_path_to_data_uri(image_path) if image_path else None
    if image_uri:
        image_html = f"""
            <img src="{image_uri}" style="
                width:96px;
                height:96px;
                border-radius:999px;
                object-fit:cover;
                flex-shrink:0;
                box-shadow:0 8px 18px rgba(17,24,39,0.12);
            ">
        """
    strength_style = strength_chip_style(strength)
    return f"""
    <div style="
        display:flex;
        gap:14px;
        align-items:flex-start;
        background:#ffffff;
        border:1px solid #e7eaf3;
        border-radius:16px;
        padding:14px 16px;
        box-shadow: 0 8px 18px rgba(17,24,39,0.05);
        margin-bottom:14px;
    ">
        <div style="
            width:30px;
            height:30px;
            border-radius:8px;
            background:#4caf50;
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
                <div style="font-size:24px; font-weight:800; color:#2f3240;">
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
            </div>
            <div style="margin-top:8px; font-size:14px; line-height:1.55; color:#4b5563;">
                {html.escape(display_value(description))}
            </div>
        </div>
    </div>
    """


# -----------------------
# LOAD DATA (multi-country)
# -----------------------
DATA_DIR = Path("data")
PRODUCER_FILES = ["producers.csv", "malta_producers.csv"]
CREATOR_FILES = ["creators.csv", "local_market_creators.csv"]
TREND_FILES = ["trends.csv", "local_market_trends.csv"]
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
    return pd.read_csv(path, keep_default_na=False).replace({"": "N/A"}).fillna("N/A")


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


def _country_folders():
    if not DATA_DIR.exists():
        return []
    return sorted(
        p for p in DATA_DIR.iterdir()
        if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
    )


def load_country_registry() -> pd.DataFrame:
    path = DATA_DIR / "countries.csv"
    if path.exists():
        registry = pd.read_csv(path)
        registry["code"] = registry["code"].astype(str).str.strip()
        return registry
    return pd.DataFrame(columns=["code", "name", "latitude", "longitude", "zoom"])


def load_all_market_data():
    registry = load_country_registry()
    producers, creators, trends, neighbourhoods = [], [], [], []

    folders = _country_folders()
    if not folders:
        # Legacy layout: CSVs in the project root, treated as Malta.
        root = Path(".")
        prod = _first_existing(root, PRODUCER_FILES)
        if prod:
            producers.append(_ensure_country(_read_csv(prod), "MLT"))
        crea = _first_existing(root, CREATOR_FILES)
        if crea:
            creators.append(_ensure_country(_read_csv(crea), "MLT"))
        tren = _first_existing(root, TREND_FILES)
        if tren:
            trends.append(_ensure_country(_read_csv(tren), "MLT"))
        demo = _first_existing(root, NEIGHBOURHOOD_FILES)
        if demo:
            neighbourhoods.append(_ensure_country(_read_csv(demo), "MLT"))
        if registry.empty:
            registry = pd.DataFrame(
                [{"code": "MLT", "name": "Malta", "latitude": 35.94, "longitude": 14.40, "zoom": 9}]
            )
    else:
        for folder in folders:
            code = folder.name
            prod = _first_existing(folder, PRODUCER_FILES)
            if prod:
                producers.append(_ensure_country(_read_csv(prod), code))
            crea = _first_existing(folder, CREATOR_FILES)
            if crea:
                creators.append(_ensure_country(_read_csv(crea), code))
            tren = _first_existing(folder, TREND_FILES)
            if tren:
                trends.append(_ensure_country(_read_csv(tren), code))
            demo = _first_existing(folder, NEIGHBOURHOOD_FILES)
            if demo:
                neighbourhoods.append(_ensure_country(_read_csv(demo), code))
            if registry.empty or code not in set(registry["code"].astype(str)):
                extra = pd.DataFrame(
                    [{"code": code, "name": code, "latitude": "", "longitude": "", "zoom": ""}]
                )
                registry = pd.concat([registry, extra], ignore_index=True)

    return (
        registry,
        _concat(producers),
        _concat(creators),
        _concat(trends),
        _concat(neighbourhoods),
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


registry_df, all_producers_df, all_creators_df, all_trends_df, all_demographics_df = load_all_market_data()

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
st.sidebar.title("Filters")
selected_country_label = st.sidebar.selectbox("Country", country_options, index=default_country_index)
selected_country_code = None if selected_country_label == "All countries" else label_to_code.get(selected_country_label)

df = all_producers_df.copy()
creators_df = all_creators_df.copy()
trends_df = all_trends_df.copy()
demographics_df = all_demographics_df.copy()

if selected_country_code:
    df = df[df["Country"].astype(str) == selected_country_code]
    if not creators_df.empty and "Country" in creators_df.columns:
        creators_df = creators_df[creators_df["Country"].astype(str) == selected_country_code]
    if not trends_df.empty and "Country" in trends_df.columns:
        trends_df = trends_df[trends_df["Country"].astype(str) == selected_country_code]
    if not demographics_df.empty and "Country" in demographics_df.columns:
        demographics_df = demographics_df[demographics_df["Country"].astype(str) == selected_country_code]
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

if not creators_df.empty and "Name / Handle" in creators_df.columns:
    creators_df["Profile Pic"] = creators_df["Name / Handle"].apply(resolve_creator_pic)

neighbourhoods = ["All"] + sorted(df["Neighbourhood"].dropna().astype(str).unique().tolist())
selected_neighbourhood = st.sidebar.selectbox("Neighbourhood", neighbourhoods)

categories = ["All"] + sorted(df["Category"].dropna().astype(str).unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

search_term = st.sidebar.text_input("Search Producer")
show_only_mapped = st.sidebar.checkbox("Show only rows with coordinates", value=False)

# -----------------------
# FILTER DATA
# -----------------------
filtered_df = df.copy()

if selected_neighbourhood != "All":
    filtered_df = filtered_df[filtered_df["Neighbourhood"] == selected_neighbourhood]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if search_term:
    filtered_df = filtered_df[
        filtered_df["Producer"].astype(str).str.contains(search_term, case=False, na=False)
    ]

if show_only_mapped:
    filtered_df = filtered_df.dropna(subset=["Latitude_num", "Longitude_num"])

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

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(clean_html(top_metric_card("Total Producers", len(filtered_df), "Across all neighbourhoods", icon=ICON_USERS, icon_bg="#EDEBFF", icon_color="#6F5CFF", card_bg="#F5F3FF")), unsafe_allow_html=True)
    with kpi2:
        st.markdown(clean_html(top_metric_card("Neighbourhoods", filtered_df["Neighbourhood"].nunique(), f"Across {MARKET_NAME}", icon=ICON_MAP_PIN, icon_bg="#E5F0FF", icon_color="#2F6BFF", card_bg="#EFF6FF")), unsafe_allow_html=True)
    with kpi3:
        st.markdown(clean_html(top_metric_card("Categories", filtered_df["Category"].nunique(), "Artisanal categories", icon=ICON_GRID, icon_bg="#E6F7EC", icon_color="#48B26B", card_bg="#F0FBF3")), unsafe_allow_html=True)
    with kpi4:
        st.markdown(clean_html(top_metric_card("Mapped Rows", len(filtered_map_df), "Have coordinates", icon=ICON_MAP, icon_bg="#FFF3E0", icon_color="#F4A94E", card_bg="#FFFBF0")), unsafe_allow_html=True)

    st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

    if selected_neighbourhood != "All" and not demographics_df.empty:
        demo_match = demographics_df[demographics_df["Neighbourhood"] == selected_neighbourhood]
        if not demo_match.empty:
            st.markdown(
                clean_html(render_neighbourhood_demographic_card(demo_match.iloc[0])),
                unsafe_allow_html=True,
            )
            st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

    top_left, top_right = st.columns(2, gap="large")
    with top_left:
        st.subheader("Top Categories")
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

    if not map_counts.empty:
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
            zoom=MAP_ZOOM,
            center=MAP_CENTER,
            height=MAP_HEIGHT,
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

    st.caption(
        f"Showing {len(display_df)} of {len(scored_df)} producers "
        f"across {display_df['Neighbourhood'].nunique() if 'Neighbourhood' in display_df.columns else 0} neighbourhoods. "
        "Google rating and review filters stay off at 0, because most producers are not rated yet."
    )
    st.dataframe(
        display_df.reset_index(drop=True),
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
    st.caption(f"Creator signals and emerging food & drink trends across {MARKET_NAME}")

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

        top_strength = "Strong"
        top_trend_label = "—"
        if not trends_df.empty and "Strength" in trends_df.columns:
            top_strength = strength_score_label(trends_df.iloc[0]["Strength"])
        if not trends_df.empty:
            top_trend_label = display_value(trends_df.iloc[0].get("Trend", ""))
        emerging_count = len(trends_df)

        # ---- 1) Top Trend Strength + Emerging Trends (top row, full width) ----
        strength_col1, strength_col2 = st.columns(2)
        with strength_col1:
            st.markdown(clean_html(top_metric_card("Top Trend Strength", top_strength, top_trend_label, icon=ICON_TRENDING_UP, icon_bg="#E6F7EC", icon_color="#2E9E4F", value_color="#2E9E4F", card_bg="#F0FBF3")), unsafe_allow_html=True)
        with strength_col2:
            st.markdown(clean_html(top_metric_card("Emerging Trends", emerging_count, f"Key {MARKET_NAME} themes identified", icon=ICON_LIGHTBULB, icon_bg="#FFF7E0", icon_color="#F5A623", card_bg="#FFFBF0")), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 2) Top 5 Trends (full width, one card per row) ----
        st.markdown(f"### Top 5 {MARKET_NAME} Trends")
        trends_to_show = trends_df.head(5).copy()
        for _, row in trends_to_show.iterrows():
            rank_raw = pd.to_numeric(row.get("Rank", 0), errors="coerce")
            rank = int(rank_raw) if pd.notna(rank_raw) else 0
            trend = display_value(row.get("Trend", ""))
            strength = strength_score_label(row.get("Strength", ""))
            description = display_value(row.get("Description", ""))
            image_path = resolve_trend_image(row.get("Image", ""))

            st.markdown(
                clean_html(
                    render_trend_card(
                        rank=rank,
                        trend=trend,
                        strength=strength,
                        description=description,
                        image_path=image_path,
                    )
                ),
                unsafe_allow_html=True,
            )

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 3) Total Creators + Total Followers (full width) ----
        creator_col1, creator_col2 = st.columns(2)
        with creator_col1:
            st.markdown(clean_html(top_metric_card("Total Creators", creator_count, f"Tracked {MARKET_NAME} food creators", icon=ICON_USERS, icon_bg="#E5F0FF", icon_color="#2F6BFF", card_bg="#EFF6FF")), unsafe_allow_html=True)
        with creator_col2:
            st.markdown(clean_html(top_metric_card("Total Followers", f"{total_followers:,}", "Combined audience", icon=ICON_USER_GROUP, icon_bg="#EDEBFF", icon_color="#6F5CFF", card_bg="#F5F3FF")), unsafe_allow_html=True)

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
                    color_discrete_sequence=["#6F5CFF", "#4B3AD5", "#B8ADFF"],
                )
                fig_platform.update_traces(
                    textinfo="none",
                    marker=dict(line=dict(color="white", width=2)),
                )
                fig_platform.update_layout(
                    height=300,
                    margin=dict(r=0, t=20, l=0, b=0),
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
                    background-color: #FFF7E0 !important;
                    border: 1px solid #F5E6B8 !important;
                    border-top: none !important;
                    border-radius: 0 0 16px 16px !important;
                    margin-top: -14px !important;
                }
                div[data-testid="stCode"] pre, div[data-testid="stCodeBlock"] pre {
                    background-color: transparent !important;
                    font-size: 12px !important;
                    line-height: 1.6 !important;
                }
                div[data-testid="stCode"] code, div[data-testid="stCodeBlock"] code {
                    color: #5a4a1a !important;
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

    if demographics_df.empty:
        st.info(
            "No demographic data found for this country. Add neighbourhoods.csv to the "
            "matching folder under data/ to unlock this tab."
        )
    else:
        demo_work = demographics_df.copy()
        demo_work["Spending Bucket"] = demo_work["Spending Profile"].apply(spending_bucket)
        demo_work["Tags"] = demo_work.apply(get_neighbourhood_tags, axis=1)

        # ---- 1) KPI row ----
        halal_count = demo_work["Tags"].apply(lambda t: "Halal" in t).sum()
        vegan_count = demo_work["Tags"].apply(lambda t: "Vegan / Plant-based" in t).sum()
        premium_count = demo_work["Tags"].apply(lambda t: "Premium" in t).sum()

        demo_kpi1, demo_kpi2, demo_kpi3, demo_kpi4 = st.columns(4)
        with demo_kpi1:
            st.markdown(clean_html(top_metric_card("Neighbourhoods Profiled", len(demo_work), "AI-researched overviews", icon=ICON_MAP_PIN, icon_bg="#E5F0FF", icon_color="#2F6BFF", card_bg="#EFF6FF")), unsafe_allow_html=True)
        with demo_kpi2:
            st.markdown(clean_html(top_metric_card("Halal Demand Areas", int(halal_count), "Flagged for halal range", icon=ICON_USERS, icon_bg="#E6F7EC", icon_color="#2E9E4F", card_bg="#F0FBF3")), unsafe_allow_html=True)
        with demo_kpi3:
            st.markdown(clean_html(top_metric_card("Vegan / Plant-based Areas", int(vegan_count), "Flagged for plant-based range", icon=ICON_GRID, icon_bg="#EDEBFF", icon_color="#6F5CFF", card_bg="#F5F3FF")), unsafe_allow_html=True)
        with demo_kpi4:
            st.markdown(clean_html(top_metric_card("Premium-Tier Areas", int(premium_count), "Flagged for premium range", icon=ICON_TRENDING_UP, icon_bg="#FFF3E0", icon_color="#F4A94E", card_bg="#FFFBF0")), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{TOP_ROW_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 2) Detail card for a selected neighbourhood ----
        st.subheader("Neighbourhood Deep Dive")
        selected_demo_neighbourhood = st.selectbox(
            "Select a neighbourhood",
            sorted(demo_work["Neighbourhood"].tolist()),
            key="demo_detail_select",
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

        if demo_map.empty:
            st.info("No matching coordinates found for these neighbourhoods yet.")
        else:
            fig_demo_map = px.scatter_mapbox(
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
                zoom=MAP_ZOOM,
                center=MAP_CENTER,
                height=MAP_HEIGHT,
            )
            fig_demo_map.update_traces(marker=dict(size=16))
            fig_demo_map.update_layout(
                mapbox_style="carto-positron",
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
                        display:inline-block; background:#F5F3FF; color:#6F5CFF; border:1px solid #E2DBFF;
                        font-size:13px; font-weight:700; padding:7px 14px; border-radius:999px; margin:0 8px 8px 0;
                    ">{html.escape(n)}</span>"""
                    for n in matching["Neighbourhood"].tolist()
                )
                st.markdown(
                    clean_html(f"""
                    <div style="background:#ffffff; border:1px solid #ECEEF3; border-radius:16px; padding:16px 20px; box-shadow:0 8px 20px rgba(17,24,39,0.05);">
                        <div style="font-size:12px; color:#9096a3; font-weight:600; margin-bottom:10px;">{len(matching)} MATCHING AREAS</div>
                        {chips}
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

        with mix_col:
            st.subheader("Areas by Spending Tier")
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
                showlegend=False,
            )
            st.plotly_chart(fig_bucket, use_container_width=True)
            st.markdown(clean_html(render_spend_bracket_legend()), unsafe_allow_html=True)

        st.markdown(f"<div style='height:{SECTION_GAP}px;'></div>", unsafe_allow_html=True)

        # ---- 5) Full comparison table ----
        st.subheader("All Neighbourhoods — Comparison Table")
        st.caption("Sort or search any column below — useful for cross-checking multiple areas at once before a range decision.")
        table_cols = [
            "Neighbourhood", "Dominant Segments", "Notable Communities", "Spending Profile",
            "Dietary Considerations", "Product Recommendations", "Confidence",
        ]
        st.dataframe(
            demo_work[table_cols],
            use_container_width=True,
            height=420,
        )
