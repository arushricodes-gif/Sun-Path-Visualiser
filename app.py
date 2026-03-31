import streamlit as st
import pytz
import plotly.graph_objects as go
import folium
from datetime import datetime, date, timedelta
from timezonefinder import TimezoneFinder
from astral import LocationInfo
from astral.sun import sunrise, sunset, noon, azimuth
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation, streamlit_js_eval
import datetime as dt

import visuals
import solarlogic

st.set_page_config(layout="wide", page_title="Sun Scout", page_icon="☀️")

# ── ALWAYS LIGHT THEME ────────────────────────────────────────────────────────
visuals.apply_styles("light")

# ── GPS / SESSION STATE INIT ──────────────────────────────────────────────────
if 'coords' not in st.session_state:
    st.session_state.coords        = [0.0, 0.0]
    st.session_state.gps_requested = False

_qp = st.query_params
if "cam_rot"  in _qp:
    try:    st.session_state["cam3d_rot"]  = float(_qp["cam_rot"])
    except: pass
if "cam_tilt" in _qp:
    try:    st.session_state["cam3d_tilt"] = float(_qp["cam_tilt"])
    except: pass

if "cam3d_rot"  not in st.session_state: st.session_state["cam3d_rot"]  = 0.0
if "cam3d_tilt" not in st.session_state: st.session_state["cam3d_tilt"] = 45.0
if "cam3d_zoom" not in st.session_state: st.session_state["cam3d_zoom"] = 1.3

if not st.session_state.gps_requested:
    loc = get_geolocation()
    if loc and 'coords' in loc:
        st.session_state.coords        = [loc['coords']['latitude'], loc['coords']['longitude']]
        st.session_state.gps_requested = True
        st.rerun()

lat, lon = st.session_state.coords
loc_key  = f"{lat}_{lon}"
if "last_loc_key" not in st.session_state or st.session_state.last_loc_key != loc_key:
    st.session_state.env_data     = solarlogic.get_environmental_data(lat, lon)
    st.session_state.last_loc_key = loc_key
env_data = st.session_state.env_data

tf        = TimezoneFinder()
tz_name   = tf.timezone_at(lng=lon, lat=lat) or "UTC"
local_tz  = pytz.timezone(tz_name)
city_info = LocationInfo(timezone=tz_name, latitude=lat, longitude=lon)

# ── Fixed white/orange palette ────────────────────────────────────────────────
ORG      = "#E07B00"
ORG_LT   = "#FFF3E0"
WHITE    = "#FFFFFF"
BG       = "#F8F4EF"
CARD_BDR = "rgba(224,123,0,0.18)"
TEXT_DARK= "#1A1A1A"
TEXT_MID = "#555555"
TEXT_SUB = "#888888"
_plot_font= "#1A1A1A"
_plot_grid= "rgba(0,0,0,0.07)"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

.stApp {{
    background: {BG} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {TEXT_DARK} !important;
}}
h1,h2,h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {TEXT_DARK} !important;
    font-weight: 700 !important;
}}
p, li, span, label, div {{ color: {TEXT_DARK} !important; }}

[data-testid="stSidebar"] {{
    background: {WHITE} !important;
    border-right: 2px solid {ORG_LT} !important;
    box-shadow: 2px 0 16px rgba(224,123,0,0.08) !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{
    color: {TEXT_DARK} !important;
    -webkit-text-fill-color: {TEXT_DARK} !important;
}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    font-size: 14px !important;
    font-weight: 700 !important;
    color: {TEXT_DARK} !important;
    -webkit-text-fill-color: {TEXT_DARK} !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}}

[data-testid="stTabs"] [role="tablist"] {{
    background: {WHITE} !important;
    border: 2px solid {ORG_LT} !important;
    border-radius: 16px !important;
    padding: 6px !important;
    gap: 4px !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    border-radius: 12px !important;
    color: {TEXT_MID} !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    padding: 12px 28px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    border: none !important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    background: {ORG} !important;
    color: {WHITE} !important;
    border: none !important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {{
    color: {WHITE} !important;
    -webkit-text-fill-color: {WHITE} !important;
}}
[data-testid="stTabs"] button[role="tab"] p {{ color: inherit !important; }}

.stButton > button {{
    background: {ORG} !important;
    color: {WHITE} !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 2px 12px rgba(224,123,0,0.25) !important;
    transition: all .2s !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: #C96E00 !important;
    box-shadow: 0 4px 20px rgba(224,123,0,0.35) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button p {{ color: {WHITE} !important; -webkit-text-fill-color: {WHITE} !important; }}
button[kind="secondaryFormSubmit"] {{
    background: {ORG} !important;
    color: {WHITE} !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    width: 100% !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
button[kind="secondaryFormSubmit"] p {{ color: {WHITE} !important; -webkit-text-fill-color: {WHITE} !important; }}

div[data-baseweb="input"] {{
    background: {WHITE} !important;
    border: 2px solid #E5E7EB !important;
    border-radius: 12px !important;
}}
div[data-baseweb="input"]:focus-within {{
    border-color: {ORG} !important;
    box-shadow: 0 0 0 3px rgba(224,123,0,0.12) !important;
}}
input {{
    color: {TEXT_DARK} !important;
    -webkit-text-fill-color: {TEXT_DARK} !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: transparent !important;
}}
input::placeholder {{ color: {TEXT_SUB} !important; -webkit-text-fill-color: {TEXT_SUB} !important; }}

.stSlider [data-baseweb="slider"] > div > div {{
    background: linear-gradient(90deg, {ORG_LT}, {ORG}) !important;
    height: 4px !important;
}}
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {ORG} !important;
    border: 3px solid {WHITE} !important;
    box-shadow: 0 0 0 2px {ORG} !important;
    width: 18px !important;
    height: 18px !important;
}}
[data-testid="stSliderTickBar"] {{ display: none !important; }}

[data-testid="stSelectbox"] > div > div {{
    background: {WHITE} !important;
    border: 2px solid #E5E7EB !important;
    border-radius: 12px !important;
    color: {TEXT_DARK} !important;
    font-size: 15px !important;
}}
[data-testid="stSelectbox"] span {{ color: {TEXT_DARK} !important; }}

[data-testid="stRadio"] label {{
    background: {WHITE} !important;
    border: 2px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 8px 18px !important;
    cursor: pointer !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    transition: all .15s !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    border-color: {ORG} !important;
    background: {ORG_LT} !important;
}}
[data-testid="stRadio"] label:has(input:checked) span {{
    color: {ORG} !important;
    -webkit-text-fill-color: {ORG} !important;
}}
[data-testid="stRadio"] label span {{ color: {TEXT_DARK} !important; font-size: 14px !important; }}

[data-testid="stToggle"] [data-checked="true"] {{ background: {ORG} !important; }}

[data-testid="stDateInput"] > div {{
    background: {WHITE} !important;
    border: 2px solid #E5E7EB !important;
    border-radius: 12px !important;
}}
[data-testid="stDateInput"] input {{
    color: {TEXT_DARK} !important;
    -webkit-text-fill-color: {TEXT_DARK} !important;
}}

[data-testid="stMetric"] {{
    background: {WHITE} !important;
    border: 2px solid {ORG_LT} !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    box-shadow: 0 2px 8px rgba(224,123,0,0.08) !important;
}}
[data-testid="stMetricValue"] {{
    color: {ORG} !important;
    -webkit-text-fill-color: {ORG} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 30px !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] p {{
    font-size: 13px !important;
    font-weight: 700 !important;
    color: {TEXT_SUB} !important;
    -webkit-text-fill-color: {TEXT_SUB} !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
}}

[data-testid="stAlert"] {{
    background: #FFF8F0 !important;
    border: 1px solid rgba(224,123,0,0.3) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
}}

.main .block-container {{ padding-top: 1.5rem !important; max-width: 1440px !important; }}
hr {{ border: none !important; height: 2px !important; background: {ORG_LT} !important; }}

::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: rgba(224,123,0,0.25); border-radius: 4px; }}

.js-plotly-plot .plotly .bg {{ fill: transparent !important; }}
.leaflet-control-attribution, .osmb-attribution {{ display: none !important; }}

[data-testid="stSidebar"] [data-testid="stButton"] {{
    display: flex !important;
    justify-content: center !important;
}}
[data-testid="stSidebar"] [data-testid="stButton"] button {{
    width: auto !important;
    padding: 10px 32px !important;
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:24px 0 16px;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:64px;font-weight:900;
             color:{ORG} !important;-webkit-text-fill-color:{ORG} !important;
             letter-spacing:8px;line-height:1;
             text-shadow:0 2px 12px rgba(224,123,0,0.18);">☀️ SUN<br>SCOUT</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;font-weight:600;
             color:{TEXT_SUB} !important;-webkit-text-fill-color:{TEXT_SUB} !important;
             letter-spacing:4px;text-transform:uppercase;margin-top:6px;">
             Visualize the Light</div>
    </div>
    <div style="height:2px;background:{ORG_LT};border-radius:2px;margin:0 0 20px;"></div>
    """, unsafe_allow_html=True)

    st.warning("💻 Best viewed on laptop/PC.")

    st.markdown(f"""
    <div style="font-size:16px;font-weight:800;color:{ORG};
         font-family:'Space Grotesk',sans-serif;margin:16px 0 10px;">
         📍 Location</div>
    """, unsafe_allow_html=True)

    with st.form("city_search"):
        search_query = st.text_input("Search for a place", placeholder="e.g. Paris, France")
        submitted    = st.form_submit_button("🔍 Search")
        if submitted and search_query:
            coords = solarlogic.search_city(search_query)
            if coords:
                st.session_state.coords = coords
                st.rerun()
            else:
                st.error("Location not found.")

    if st.button("📍 Use My GPS"):
        st.session_state.gps_requested = False
        st.rerun()

    st.markdown(f"""
    <div style="background:{ORG_LT};border:1px solid {CARD_BDR};border-radius:10px;
         padding:10px 14px;margin:8px 0 20px;font-size:13px;color:{TEXT_MID};
         font-family:'Plus Jakarta Sans',sans-serif;">
        📌 <b style="color:{TEXT_DARK};">{lat:.4f}°, {lon:.4f}°</b>
    </div>
    <div style="height:2px;background:{ORG_LT};border-radius:2px;margin:0 0 16px;"></div>
    """, unsafe_allow_html=True)

    celestial_dates = {
        "Manual Selection":            None,
        "🌸 Spring Equinox (Mar 20)":  date(2026, 3, 20),
        "☀️ Summer Solstice (Jun 21)": date(2026, 6, 21),
        "🍂 Autumn Equinox (Sep 22)":  date(2026, 9, 22),
        "❄️ Winter Solstice (Dec 21)": date(2026, 12, 21),
    }
    date_preset = st.selectbox("Key Dates", list(celestial_dates.keys()))
    target_date = st.date_input("Custom Date", date.today()) \
                  if date_preset == "Manual Selection" else celestial_dates[date_preset]

    shour = st.slider("Hour",   0, 23, datetime.now(local_tz).hour)
    smin  = st.slider("Minute", 0, 59, 0, step=5)
    sim_time = local_tz.localize(
        datetime.combine(target_date, datetime.min.time())
    ) + timedelta(hours=shour, minutes=smin)



    radius_meters = 250
    enable_aqi    = False  # removed

# ── SUN TIMES ─────────────────────────────────────────────────────────────────
try:
    rise_t = sunrise(city_info.observer, date=target_date, tzinfo=local_tz)
    set_t  = sunset(city_info.observer,  date=target_date, tzinfo=local_tz)
    noon_t = noon(city_info.observer,    date=target_date, tzinfo=local_tz)
except Exception:
    rise_t = sim_time.replace(hour=6,  minute=0)
    set_t  = sim_time.replace(hour=18, minute=0)
    noon_t = sim_time.replace(hour=12, minute=0)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def build_path_data():
    pts, curr = [], rise_t
    while curr <= set_t:
        slat, slon, shlat, shlon, az, el = solarlogic.get_solar_pos(
            city_info, curr, radius_meters, lat, lon)
        pts.append({"lat": slat, "lon": slon, "shlat": shlat, "shlon": shlon,
                    "time": curr.strftime("%H:%M"), "el": el, "az": az,
                    "iso": curr.isoformat()})
        curr += timedelta(minutes=10)
    return pts


def render_metrics_and_chart(key_suffix):
    st.markdown(f"<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:16px;font-weight:800;color:{ORG};
         font-family:'Space Grotesk',sans-serif;margin:8px 0 12px;">
         📊 Solar Data for Selected Time</div>
    """, unsafe_allow_html=True)

    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(
        city_info, sim_time, radius_meters, lat, lon)
    radiation_wm2 = solarlogic.calculate_solar_radiation(m_el)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🕐 Time",       sim_time.strftime('%H:%M'))
    c2.metric("🧭 Azimuth",    f"{m_az:.1f}°")
    c3.metric("☀️ Elevation",  f"{m_el:.1f}°")
    c4.metric("🌞 Solar Noon", noon_t.strftime('%H:%M'))

    path_pts, tmp = [], rise_t
    while tmp <= set_t:
        _, _, _, _, _, el = solarlogic.get_solar_pos(city_info, tmp, radius_meters, lat, lon)
        path_pts.append({"time": tmp.strftime("%H:%M"), "el": el})
        tmp += timedelta(minutes=15)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[p['time'] for p in path_pts],
        y=[p['el']   for p in path_pts],
        mode='lines',
        line=dict(color=ORG, width=3),
        fill='tozeroy',
        fillcolor='rgba(224,123,0,0.08)',
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=_plot_font,
        xaxis=dict(showgrid=False, color=TEXT_SUB, tickfont=dict(size=11, color=TEXT_SUB)),
        yaxis=dict(showgrid=True, gridcolor=_plot_grid,
                   title="Elevation °", color=TEXT_SUB,
                   tickfont=dict(size=11, color=TEXT_SUB))
    )
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")


# ── CARD CSS ──────────────────────────────────────────────────────────────────
_CARD_CSS = f"""
<style>
.sc-card {{
    background: {WHITE};
    border: 2px solid {ORG_LT};
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 16px rgba(224,123,0,0.06);
}}
.sc-section {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: {TEXT_DARK} !important;
    -webkit-text-fill-color: {TEXT_DARK} !important;
    margin: 28px 0 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.sc-section::after {{
    content: '';
    flex: 1;
    height: 2px;
    background: {ORG_LT};
    border-radius: 2px;
}}
.sc-pill {{
    display: inline-block;
    background: {ORG_LT};
    color: {ORG} !important;
    -webkit-text-fill-color: {ORG} !important;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
    margin-top: 8px;
    border: 1px solid rgba(224,123,0,0.2);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
</style>
"""

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_info, tab_explorer = st.tabs(["📖 Getting Started", "☀️ Sun Scout"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — GETTING STARTED
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown(_CARD_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <style>
    .hero {{
        background: linear-gradient(135deg, #FFF8F0 0%, #FFF3E0 60%, #FFE0B2 100%);
        border: 2px solid rgba(224,123,0,0.15);
        border-radius: 24px;
        padding: 56px 52px 52px;
        position: relative;
        overflow: hidden;
        margin-bottom: 32px;
    }}
    .hero::before {{
        content: '☀️';
        position: absolute;
        right: 52px; top: 50%;
        transform: translateY(-50%);
        font-size: 140px;
        opacity: 0.12;
        filter: blur(3px);
        line-height: 1;
        user-select: none;
    }}
    .hero-tag {{
        display: inline-block;
        background: {ORG};
        color: #fff !important;
        -webkit-text-fill-color: #fff !important;
        font-size: 11px;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 20px;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: 18px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2.4rem, 4.5vw, 3.8rem);
        font-weight: 800;
        color: {TEXT_DARK} !important;
        -webkit-text-fill-color: {TEXT_DARK} !important;
        line-height: 1.1;
        margin-bottom: 16px;
    }}
    .hero-title .accent {{
        color: {ORG} !important;
        -webkit-text-fill-color: {ORG} !important;
    }}
    .hero-desc {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.2rem;
        font-weight: 400;
        color: {TEXT_MID} !important;
        -webkit-text-fill-color: {TEXT_MID} !important;
        max-width: 520px;
        line-height: 1.8;
    }}
    .steps-row {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }}
    .step-card {{
        background: {WHITE};
        border: 2px solid {ORG_LT};
        border-radius: 18px;
        padding: 24px 20px;
        box-shadow: 0 2px 12px rgba(224,123,0,0.06);
    }}
    .step-num {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: {ORG};
        opacity: .15;
        line-height: 1;
        margin-bottom: 8px;
    }}
    .step-icon {{ font-size: 28px; margin-bottom: 10px; display: block; }}
    .step-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: {ORG} !important;
        -webkit-text-fill-color: {ORG} !important;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: .04em;
    }}
    .step-body {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.0rem;
        line-height: 1.7;
        color: {TEXT_MID} !important;
        -webkit-text-fill-color: {TEXT_MID} !important;
    }}
    .usecase-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }}
    .usecase-card {{
        background: {WHITE};
        border: 2px solid {ORG_LT};
        border-radius: 18px;
        padding: 24px;
        display: flex;
        gap: 16px;
        align-items: flex-start;
        box-shadow: 0 2px 12px rgba(224,123,0,0.06);
    }}
    .usecase-icon {{
        font-size: 30px;
        width: 56px; height: 56px;
        background: {ORG_LT};
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }}
    .usecase-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: {ORG} !important;
        -webkit-text-fill-color: {ORG} !important;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: .04em;
    }}
    .usecase-body {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.0rem;
        line-height: 1.7;
        color: {TEXT_MID} !important;
        -webkit-text-fill-color: {TEXT_MID} !important;
    }}
    .glossary-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 14px;
        margin-bottom: 32px;
    }}
    .glossary-item {{
        background: {WHITE};
        border: 2px solid {ORG_LT};
        border-radius: 16px;
        padding: 18px 20px;
        display: flex;
        gap: 14px;
    }}
    .glossary-key {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: {ORG} !important;
        -webkit-text-fill-color: {ORG} !important;
        white-space: nowrap;
        min-width: 110px;
    }}
    .glossary-val {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.0rem;
        line-height: 1.65;
        color: {TEXT_MID} !important;
        -webkit-text-fill-color: {TEXT_MID} !important;
    }}
    @media (max-width: 900px) {{
        .steps-row {{ grid-template-columns: repeat(2,1fr); }}
        .usecase-grid {{ grid-template-columns: 1fr; }}
        .glossary-grid {{ grid-template-columns: 1fr; }}
        .hero::before {{ display: none; }}
    }}
    </style>

    <div class="hero">
        <div class="hero-tag">☀️ Sun Scout · Solar Intelligence</div>
        <div class="hero-title">Know Your <span class="accent">Sunlight</span><br>Before You Buy.</div>
        <div class="hero-desc">
            The tool built for one question every house hunter should ask —
            <em>when does sunlight actually hit that balcony?</em>
        </div>
    </div>

    <div class="sc-section">How to Use</div>
    <div class="steps-row">
        <div class="step-card">
            <div class="step-num">01</div>
            <span class="step-icon">📍</span>
            <div class="step-title">Set Your Location</div>
            <div class="step-body">Go to the Sun Scout tab, choose <b>Set Location</b>, and click on the map to drop your pin on any property.</div>
        </div>
        <div class="step-card">
            <div class="step-num">02</div>
            <span class="step-icon">🗓️</span>
            <div class="step-title">Pick a Date & Time</div>
            <div class="step-body">Use the sidebar sliders or pick a celestial preset — Summer Solstice, Winter Solstice, or any custom date.</div>
        </div>
        <div class="step-card">
            <div class="step-num">03</div>
            <span class="step-icon">▶️</span>
            <div class="step-title">Watch the Sun Move</div>
            <div class="step-body">Switch to <b>Live View</b>. Toggle between 2D map and 3D buildings. Hit Animate to watch the sun travel with real shadows.</div>
        </div>
        <div class="step-card">
            <div class="step-num">04</div>
            <span class="step-icon">🔄</span>
            <div class="step-title">Compare Seasons</div>
            <div class="step-body">Switch to <b>Year Summary</b> to see all four seasonal sun paths overlaid on the same map at once.</div>
        </div>
    </div>

    <div class="sc-section">Who Is This For</div>
    <div class="usecase-grid">
        <div class="usecase-card">
            <div class="usecase-icon">🏡</div>
            <div>
                <div class="usecase-title">House Hunters</div>
                <div class="usecase-body">That "sunny south-facing balcony" might be shaded by the building next door from October to March. Check before you sign.</div>
                <span class="sc-pill">Core Use Case</span>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">🌿</div>
            <div>
                <div class="usecase-title">Gardeners</div>
                <div class="usecase-body">Full-sun plants need 6+ hours of direct light. Watch sunlight move across your garden plot hour by hour.</div>
                <span class="sc-pill">Planting Decisions</span>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">⚡</div>
            <div>
                <div class="usecase-title">Solar Panel Owners</div>
                <div class="usecase-body">Check peak solar radiation hours by season and see if your roof gets enough sun for viable solar generation.</div>
                <span class="sc-pill">Energy Planning</span>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">📸</div>
            <div>
                <div class="usecase-title">Photographers</div>
                <div class="usecase-body">Find the exact azimuth and elevation of the sun at your shoot location — down to the minute.</div>
                <span class="sc-pill">Shot Planning</span>
            </div>
        </div>
    </div>

    <div class="sc-section">Understanding the Numbers</div>
    <div class="glossary-grid">
        <div class="glossary-item">
            <div class="glossary-key">Azimuth</div>
            <div class="glossary-val">Compass direction of the sun. North = 0°, East = 90°, South = 180°, West = 270°.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Elevation</div>
            <div class="glossary-val">How high the sun is above the horizon. 0° = just risen. 90° = directly overhead. Low = long shadows.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Solar Noon</div>
            <div class="glossary-val">The moment the sun peaks for the day — highest elevation, shortest shadows. Not always 12:00.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Radiation W/m²</div>
            <div class="glossary-val">Estimated sunlight intensity. Above 600 W/m² is strong solar generation territory.</div>
        </div>
    </div>

    <div style="background:{ORG_LT};border:2px solid rgba(224,123,0,0.15);
         border-radius:16px;padding:20px 24px;display:flex;gap:16px;align-items:center;">
        <div style="font-size:26px;flex-shrink:0;">🔬</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.95rem;
             color:{TEXT_MID} !important;-webkit-text-fill-color:{TEXT_MID} !important;line-height:1.65;">
            Sun Scout uses the <b style="color:{ORG};">Astral</b> library for precise astronomical
            calculations, <b style="color:{ORG};">OpenStreetMap</b> for building geometry, and the
            <b style="color:{ORG};">Overpass API</b> for real building heights.
            Solar positions are accurate to within fractions of a degree.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUN SCOUT EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab_explorer:
    st.markdown(_CARD_CSS, unsafe_allow_html=True)

    # View selector
    view_mode = st.radio(
        "view",
        ["📍 Set Location", "🌞 Sun Path", "🔄 Year Summary"],
        horizontal=True, key="view_mode", label_visibility="collapsed"
    )

    path_data = build_path_data()
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(
        city_info, sim_time, radius_meters, lat, lon)

    if m_el <= 0:
        st.warning(f"🌅 The sun is below the horizon at this time ({m_el:.1f}°). Try adjusting the Hour slider.")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── VIEW BRANCHES ─────────────────────────────────────────────────────────
    if view_mode == "📍 Set Location":
        _slc1, _slc2 = st.columns([4, 1])
        with _slc1:
            st.markdown(f"""
            <div style="background:{ORG_LT};border:2px solid rgba(224,123,0,0.2);
                 border-radius:14px;padding:14px 22px;margin-bottom:14px;
                 font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;
                 color:{TEXT_DARK};font-weight:500;">
                👆 <b>Click anywhere on the map</b> to set your location.
                Then switch to <b style="color:{ORG};">🌞 Sun Path</b> to see the sun path.
            </div>
            """, unsafe_allow_html=True)
        with _slc2:
            pass  # AQI removed

        map_key = f"map_setup_{target_date}_{lat}_{lon}"
        m = folium.Map(location=st.session_state.coords, zoom_start=17, tiles=None)
        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri', name='🛰 Satellite').add_to(m)
        folium.TileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='OpenStreetMap', name='🗺 Street').add_to(m)
        folium.LayerControl(position='topleft', collapsed=False).add_to(m)
        folium.Marker(
            st.session_state.coords,
            icon=folium.Icon(color='orange', icon='sun', prefix='fa'),
            tooltip=f"📍 {lat:.5f}, {lon:.5f}"
        ).add_to(m)
        map_data = st_folium(m, height=530, use_container_width=True, key=map_key)
        if map_data and map_data.get("last_clicked"):
            new_coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
            if new_coords != st.session_state.coords:
                st.session_state.coords = new_coords
                st.rerun()

    elif view_mode == "🌞 Sun Path":
        rise_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, rise_t), radius_meters)
        set_edge  = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, set_t),  radius_meters)

        # Controls above the map
        if "live_view_type" not in st.session_state:
            st.session_state.live_view_type = "3d"

        # Animate toggle — centered
        _ca, _cb, _cc = st.columns([2, 1, 2])
        with _cb:
            animate_trigger = st.toggle("▶ Animate Sun Path", value=True, key="anim_toggle_live")

        # Map style — right aligned
        _ma, _mb = st.columns([3, 2])
        with _mb:
            live_view_type = st.radio(
                "mapstyle",
                ["🏙 3D Shadow", "🗺 2D View"],
                horizontal=True, key="live_view_radio", label_visibility="collapsed",
                index=0 if st.session_state.live_view_type == "3d" else 1
            )
            st.session_state.live_view_type = "3d" if live_view_type == "🏙 3D Shadow" else "2d"

        # HUD above map
        st.markdown(f"""
        <div style="background:#fff;border:2px solid #FFF3E0;border-radius:14px;
             padding:12px 22px;margin-bottom:10px;display:flex;gap:28px;flex-wrap:wrap;
             align-items:center;box-shadow:0 2px 8px rgba(224,123,0,0.06);
             font-family:'Plus Jakarta Sans',sans-serif;">
            <span style="font-size:14px;font-weight:600;color:#888;">
                📅 <b style="color:#1A1A1A;">{target_date.strftime('%b %d, %Y')}</b></span>
            <span style="font-size:14px;font-weight:600;color:#888;">
                🌅 Sunrise <b style="color:#E07B00;font-size:16px;">{rise_t.strftime('%H:%M')}</b></span>
            <span style="font-size:14px;font-weight:600;color:#888;">
                🌇 Sunset <b style="color:#E07B00;font-size:16px;">{set_t.strftime('%H:%M')}</b></span>
            <span style="font-size:14px;font-weight:600;color:#888;">
                ☀️ Solar Noon <b style="color:#E07B00;font-size:16px;">{noon_t.strftime('%H:%M')}</b></span>
        </div>
        """, unsafe_allow_html=True)

        visuals.render_live_component(
            lat, lon, radius_meters, path_data, animate_trigger, sim_time,
            m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
            rise_edge, set_edge,
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"),
            init_view=st.session_state.get("live_view_type", "3d"),
            init_rot=st.session_state["cam3d_rot"],
            init_tilt=st.session_state["cam3d_tilt"],
            init_zoom=st.session_state["cam3d_zoom"],
        )

    else:  # Year Summary
        st.markdown(f"""
        <div style="background:{WHITE};border:2px solid {ORG_LT};border-radius:14px;
             padding:16px 24px;margin-bottom:14px;">
            <div style="font-size:1.5rem;font-weight:800;color:{TEXT_DARK};
                 font-family:'Space Grotesk',sans-serif;">
                🔄 Seasonal Sun Path Comparison</div>
            <div style="font-size:14px;color:{TEXT_SUB};margin-top:4px;
                 font-family:'Plus Jakarta Sans',sans-serif;">
                All four seasons overlaid on the same map for your location</div>
        </div>
        """, unsafe_allow_html=True)

        milestones = [
            {"id": "Summer", "date": date(2026, 6, 21)},
            {"id": "Autumn", "date": date(2026, 10, 31)},
            {"id": "Spring", "date": date(2026, 3, 20)},
            {"id": "Winter", "date": date(2026, 12, 21)},
        ]
        seasonal_data = {}
        for ms in milestones:
            m_r = sunrise(city_info.observer, date=ms["date"], tzinfo=local_tz)
            m_s = sunset(city_info.observer,  date=ms["date"], tzinfo=local_tz)
            pts, c = [], m_r
            while c <= m_s:
                lp, lop, _, _, _, _ = solarlogic.get_solar_pos(city_info, c, radius_meters, lat, lon)
                pts.append([lp, lop])
                c += timedelta(minutes=20)
            seasonal_data[ms["id"]] = {"coords": pts, "label": ms["id"]}
        visuals.render_seasonal_map(lat, lon, radius_meters, seasonal_data)

        st.markdown(f"""
        <div style="display:flex;justify-content:center;gap:32px;flex-wrap:wrap;
             background:{WHITE};padding:14px 24px;border-radius:12px;margin-top:10px;
             border:2px solid {ORG_LT};">
            <div style="display:flex;align-items:center;gap:8px;font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;">
                <span style="display:inline-block;width:28px;height:4px;background:#FF4444;border-radius:2px;"></span>
                <span style="color:#FF4444 !important;-webkit-text-fill-color:#FF4444 !important;">Summer</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;">
                <span style="display:inline-block;width:28px;height:4px;background:#FF8C00;border-radius:2px;"></span>
                <span style="color:#FF8C00 !important;-webkit-text-fill-color:#FF8C00 !important;">Autumn</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;">
                <span style="display:inline-block;width:28px;height:4px;background:#C8A800;border-radius:2px;"></span>
                <span style="color:#C8A800 !important;-webkit-text-fill-color:#C8A800 !important;">Spring</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;">
                <span style="display:inline-block;width:28px;height:4px;background:#5BAED8;border-radius:2px;"></span>
                <span style="color:#5BAED8 !important;-webkit-text-fill-color:#5BAED8 !important;">Winter</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
