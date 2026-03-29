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

st.set_page_config(layout="wide", page_title="Solar Path Visualizer", page_icon="☀️")

# ── THEME STATE ───────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

visuals.apply_styles(st.session_state.theme)

# ── GPS / SESSION STATE INIT ──────────────────────────────────────────────────
if 'coords' not in st.session_state:
    st.session_state.coords         = [0.0, 0.0]
    st.session_state.gps_requested  = False

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
        st.session_state.coords      = [loc['coords']['latitude'], loc['coords']['longitude']]
        st.session_state.gps_requested = True
        st.rerun()

lat, lon = st.session_state.coords
loc_key  = f"{lat}_{lon}"
if "last_loc_key" not in st.session_state or st.session_state.last_loc_key != loc_key:
    st.session_state.env_data    = solarlogic.get_environmental_data(lat, lon)
    st.session_state.last_loc_key = loc_key
env_data = st.session_state.env_data

tf      = TimezoneFinder()
tz_name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
local_tz  = pytz.timezone(tz_name)
city_info = LocationInfo(timezone=tz_name, latitude=lat, longitude=lon)

# ── Theme-aware colours ───────────────────────────────────────────────────────
_is_light    = st.session_state.theme == "light"
_card_bg     = "rgba(255,255,255,0.85)" if _is_light else "rgba(20, 24, 32, 0.5)"
_card_border = "rgba(212,134,10,.18)"   if _is_light else "rgba(243, 156, 18, 0.15)"
_header_col  = "#C47A0C"                if _is_light else "#F39C12"
_sub_col     = "#6B7280"                if _is_light else "#9CA3AF"
_body_col    = "#111111"                if _is_light else "#D1D5DB"
_hl_col      = "#C47A0C"                if _is_light else "#F39C12"
_plot_bg     = st.session_state.get("_plot_bg",   "rgba(0,0,0,0)")
_plot_grid   = st.session_state.get("_plot_grid", "rgba(0,0,0,0.1)")
_plot_font   = st.session_state.get("_plot_font", "#F0F2F5")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    _sidebar_text = "#111111" if _is_light else "#FFFFFF"
    _title_glow   = "rgba(180,110,0,0.3)" if _is_light else "rgba(243,156,18,0.4)"

    st.markdown(f"""
        <style>
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .flowstate-subtitle {{
            opacity: 1 !important;
            color: {_sidebar_text} !important;
            -webkit-text-fill-color: {_sidebar_text} !important;
        }}
        /* Bigger sidebar widget labels */
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            font-size: 14px !important;
            font-weight: 600 !important;
            letter-spacing: .03em !important;
            text-transform: none !important;
            color: {_sidebar_text} !important;
            -webkit-text-fill-color: {_sidebar_text} !important;
        }}
        [data-testid="stSidebar"] [data-testid="stSelectbox"] label,
        [data-testid="stSidebar"] [data-testid="stTextInput"] label,
        [data-testid="stSidebar"] [data-testid="stDateInput"] label,
        [data-testid="stSidebar"] [data-testid="stToggle"] label {{
            font-size: 14px !important;
            font-weight: 600 !important;
            color: {_sidebar_text} !important;
            -webkit-text-fill-color: {_sidebar_text} !important;
        }}
        /* Center the GPS button */
        [data-testid="stSidebar"] [data-testid="stButton"] {{
            display: flex !important;
            justify-content: center !important;
        }}
        [data-testid="stSidebar"] [data-testid="stButton"] button {{
            width: auto !important;
            padding: 10px 28px !important;
        }}
        .flowstate-title {{
            font-family:'Akira',sans-serif; font-size:80px; font-weight:900;
            text-align:center; text-transform:uppercase; letter-spacing:15px; line-height:1.1;
            margin-bottom:10px;
            background: linear-gradient(180deg, #F39C12 0%, #FFD06D 50%, #D35400 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0px 0px 20px {_title_glow});
        }}
        .flowstate-subtitle {{
            font-family:'Poppins',sans-serif;
            color: {_sidebar_text} !important;
            -webkit-text-fill-color: {_sidebar_text} !important;
            text-align:center;
            font-size:1.2rem; font-weight:300; letter-spacing:4px; text-transform:uppercase;
            margin-top:-20px; margin-bottom:30px;
            opacity: 1 !important;
            display: block !important;
        }}
        </style>

        <h1 class="flowstate-title">SUN<br>SCOUT</h1>
        <p class="flowstate-subtitle">Visualize the Light</p>
    """, unsafe_allow_html=True)

    # Theme toggle
    st.markdown(f"""
        <div style="margin-bottom:8px;font-size:14px;font-weight:600;
             color:{_sidebar_text};font-family:'Inter',sans-serif;">
            Appearance
        </div>
    """, unsafe_allow_html=True)

    _tc1, _tc2 = st.columns(2)
    with _tc1:
        if st.button("🌙  Dark", key="btn_dark",
                     type="primary" if not _is_light else "secondary"):
            st.session_state.theme = "dark"
            st.rerun()
    with _tc2:
        if st.button("☀️  Light", key="btn_light",
                     type="primary" if _is_light else "secondary"):
            st.session_state.theme = "light"
            st.rerun()

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    st.warning("Best viewed on laptop/PC.")
    st.header("⚙️ Settings")

    with st.form("city_search"):
        search_query = st.text_input("🔍 Search for place", placeholder="e.g. Paris, France")
        submitted    = st.form_submit_button("Search Location")
        if submitted and search_query:
            coords = solarlogic.search_city(search_query)
            if coords:
                st.session_state.coords = coords
                st.rerun()
            else:
                st.error("Location not found.")

    if st.button("📍 Reset to My GPS"):
        st.session_state.gps_requested = False
        st.rerun()

    celestial_dates = {
        "Manual Selection":          None,
        "Spring Equinox (Mar 20)":   date(2026, 3, 20),
        "Summer Solstice (Jun 21)":  date(2026, 6, 21),
        "Autumnal Equinox (Sep 22)": date(2026, 9, 22),
        "Winter Solstice (Dec 21)":  date(2026, 12, 21),
    }
    date_preset = st.selectbox("Key Celestial Dates", list(celestial_dates.keys()))
    target_date = st.date_input("Select Date", date.today()) if date_preset == "Manual Selection" \
                  else celestial_dates[date_preset]

    radius_meters = 250
    enable_aqi    = st.toggle("AQI and Live Weather\n(Available for live data only)", value=False)
    shour = st.slider("Hour",   0, 23, datetime.now(local_tz).hour)
    smin  = st.slider("Minute", 0, 59, 0)
    sim_time = local_tz.localize(
        datetime.combine(target_date, datetime.min.time())
    ) + timedelta(hours=shour, minutes=smin)

# ── SUN TIMES ─────────────────────────────────────────────────────────────────
try:
    rise_t = sunrise(city_info.observer, date=target_date, tzinfo=local_tz)
    set_t  = sunset(city_info.observer,  date=target_date, tzinfo=local_tz)
    noon_t = noon(city_info.observer,    date=target_date, tzinfo=local_tz)
except Exception:
    rise_t = sim_time.replace(hour=6,  minute=0)
    set_t  = sim_time.replace(hour=18, minute=0)
    noon_t = sim_time.replace(hour=12, minute=0)

# ── INFO CARD STYLES ──────────────────────────────────────────────────────────
_INFO_CARD_CSS = f"""
<style>
    .info-card {{
        background: {_card_bg};
        border: 1px solid {_card_border};
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif !important;
        backdrop-filter: blur(8px);
    }}
    .info-header {{
        font-family: 'Bebas Neue', sans-serif !important;
        color: {_header_col} !important;
        font-size: 2rem !important;
        letter-spacing: 2px !important;
        margin-bottom: 10px !important;
        text-transform: uppercase;
    }}
    .info-sub {{
        font-family: 'JetBrains Mono', monospace !important;
        color: {_sub_col} !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }}
    .highlight {{ color: {_hl_col}; font-weight: 600; }}
    .info-card p {{ color: {_body_col} !important; }}
    .info-card li {{ color: {_body_col} !important; }}
    .info-card td {{ color: {_body_col} !important; }}
</style>
"""

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
    st.markdown("---")
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(
        city_info, sim_time, radius_meters, lat, lon)
    radiation_wm2 = solarlogic.calculate_solar_radiation(m_el)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Selected Time", sim_time.strftime('%H:%M'))
    c2.metric("Azimuth",       f"{m_az:.1f}°")
    c3.metric("Elevation",     f"{m_el:.1f}°")
    c4.metric("Solar Noon",    noon_t.strftime('%H:%M'))

    if enable_aqi:
        st.markdown("#### ⚡ Live Environmental & Solar Data")
        w1, w2, w3, w4, w5 = st.columns(5)
        env = st.session_state.env_data
        w1.metric("Temp",            f"{env['temp']}°C")
        w2.metric("Humidity",        f"{env['hum']}%")
        w3.metric("Wind",            f"{env['wind']} m/s")
        w4.metric("AQI",             env["aqi"], delta=env["label"], delta_color="inverse")
        w5.metric("Solar Radiation", f"{radiation_wm2} W/m²")

    path_pts, tmp = [], rise_t
    while tmp <= set_t:
        _, _, _, _, _, el = solarlogic.get_solar_pos(city_info, tmp, radius_meters, lat, lon)
        path_pts.append({"time": tmp.strftime("%H:%M"), "el": el})
        tmp += timedelta(minutes=15)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[p['time'] for p in path_pts], y=[p['el'] for p in path_pts],
        mode='lines', line=dict(color='#f39c12', width=3),
        fill='tozeroy', fillcolor='rgba(243,156,18,0.1)'
    ))
    fig.update_layout(
        height=250, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=_plot_font,
        xaxis=dict(showgrid=False, color=_plot_font),
        yaxis=dict(showgrid=True, gridcolor=_plot_grid,
                   title="Elevation (°)", color=_plot_font)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")


# ══════════════════════════════════════════════════════════════════════════════
# TABS — just 2
# ══════════════════════════════════════════════════════════════════════════════
tab_info, tab_explorer = st.tabs(["Getting Started", "🌍 Sun Scout"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — INFO & HELP (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown(_INFO_CARD_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .hero-wrap {{
        position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 28px;
        background: {"linear-gradient(135deg, #FFF8EE 0%, #FFF3DC 60%, #FFEFC8 100%)" if _is_light else "linear-gradient(135deg, #0D0F14 0%, #141820 60%, #1a1408 100%)"};
        border: 1px solid {"rgba(212,134,10,0.25)" if _is_light else "rgba(243,156,18,0.15)"}; padding: 52px 48px 48px;
    }}
    .hero-wrap::before {{
        content: ''; position: absolute; inset: 0;
        background:
            radial-gradient(ellipse 70% 60% at 80% 50%, {"rgba(212,134,10,0.10)" if _is_light else "rgba(243,156,18,0.07)"} 0%, transparent 70%),
            radial-gradient(ellipse 40% 40% at 20% 80%, {"rgba(212,134,10,0.06)" if _is_light else "rgba(243,156,18,0.04)"} 0%, transparent 60%);
        pointer-events: none;
    }}
    .hero-eyebrow {{
        font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: .22em;
        text-transform: uppercase; color: {_header_col}; margin-bottom: 14px; opacity: 0.85;
    }}
    .hero-title {{
        font-family: 'Bebas Neue', sans-serif; font-size: clamp(2.8rem, 5vw, 4.4rem);
        letter-spacing: 3px; line-height: 1.0;
        color: {"#111111" if _is_light else "#F0F2F5"} !important;
        -webkit-text-fill-color: {"#111111" if _is_light else "#F0F2F5"} !important;
        margin-bottom: 6px;
    }}
    .hero-title span {{
        color: {_header_col} !important;
        -webkit-text-fill-color: {_header_col} !important;
    }}
    .hero-sub {{
        font-family: 'Inter', sans-serif; font-size: 1.05rem; font-weight: 300;
        color: {"#4B5563" if _is_light else "#D1D5DB"} !important;
        -webkit-text-fill-color: {"#4B5563" if _is_light else "#D1D5DB"} !important;
        margin-bottom: 32px; max-width: 520px; line-height: 1.7;
    }}
    .hero-sun-bg {{
        position: absolute; right: 48px; top: 50%; transform: translateY(-50%);
        font-size: 130px; line-height: 1; opacity: {"0.15" if _is_light else "0.12"}; pointer-events: none;
        filter: blur(2px); user-select: none;
    }}
    .steps-grid {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px;
    }}
    .step-card {{
        background: {_card_bg}; border: 1px solid {_card_border}; border-radius: 14px;
        padding: 22px 18px; position: relative;
    }}
    .step-num {{
        font-family: 'Bebas Neue', sans-serif; font-size: 3rem; letter-spacing: 2px;
        color: {_header_col}; opacity: 0.22; line-height: 1; margin-bottom: 8px;
    }}
    .step-icon {{ font-size: 26px; margin-bottom: 10px; display: block; }}
    .step-title {{
        font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 1.5px;
        color: {_header_col}; margin-bottom: 8px; text-transform: uppercase;
    }}
    .step-body {{
        font-family: 'Inter', sans-serif; font-size: 0.93rem; line-height: 1.65;
        color: {'#374151' if _is_light else '#E2E8F0'};
    }}
    .step-arrow {{
        position: absolute; top: 50%; right: -10px; transform: translateY(-50%);
        font-size: 18px; color: {_header_col}; opacity: 0.35; z-index: 2;
    }}
    .usecase-grid {{
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 28px;
    }}
    .usecase-card {{
        background: {_card_bg}; border: 1px solid {_card_border}; border-radius: 14px;
        padding: 22px 22px; display: flex; gap: 16px; align-items: flex-start;
    }}
    .usecase-icon {{
        font-size: 32px; flex-shrink: 0; width: 52px; height: 52px;
        background: rgba(243,156,18,0.08); border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid rgba(243,156,18,0.15);
    }}
    .usecase-title {{
        font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 1.5px;
        color: {_header_col}; margin-bottom: 6px; text-transform: uppercase;
    }}
    .usecase-body {{
        font-family: 'Inter', sans-serif; font-size: 0.93rem; line-height: 1.65;
        color: {'#374151' if _is_light else '#E2E8F0'};
    }}
    .usecase-tag {{
        display: inline-block; font-family: 'JetBrains Mono', monospace;
        font-size: 9px; letter-spacing: .12em; text-transform: uppercase;
        background: rgba(243,156,18,0.1); color: {_header_col};
        border: 1px solid rgba(243,156,18,0.2); border-radius: 20px;
        padding: 2px 10px; margin-top: 8px;
    }}
    .feature-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 28px; }}
    .feature-pill {{
        background: {_card_bg}; border: 1px solid {_card_border}; border-radius: 30px;
        padding: 8px 18px; font-family: 'JetBrains Mono', monospace;
        font-size: 11px; color: {'#374151' if _is_light else '#9CA3AF'};
        display: flex; align-items: center; gap: 7px;
    }}
    .feature-pill span {{ color: {_header_col}; font-size: 14px; }}
    .glossary-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    .glossary-item {{
        background: {_card_bg}; border: 1px solid {_card_border};
        border-radius: 12px; padding: 16px 18px; display: flex; gap: 12px;
    }}
    .glossary-key {{
        font-family: 'Bebas Neue', sans-serif; font-size: 1rem; letter-spacing: 1px;
        color: {_header_col}; white-space: nowrap; min-width: 90px;
    }}
    .glossary-val {{
        font-family: 'Inter', sans-serif; font-size: 0.93rem; line-height: 1.6;
        color: {'#374151' if _is_light else '#E2E8F0'};
    }}
    .section-label {{
        font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; letter-spacing: .12em;
        text-transform: uppercase; color: {_header_col};
        margin-bottom: 14px; margin-top: 20px;
    }}
    /* Force all text inside hero to respect theme colors */
    .hero-wrap .hero-eyebrow,
    .hero-wrap .hero-title,
    .hero-wrap .hero-sub {{
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }}
    /* Step cards in light mode */
    .step-body, .usecase-body, .glossary-val {{
        color: {"#374151" if _is_light else "#E2E8F0"} !important;
        -webkit-text-fill-color: {"#374151" if _is_light else "#E2E8F0"} !important;
    }}
    .step-title, .usecase-title, .glossary-key {{
        color: {_header_col} !important;
        -webkit-text-fill-color: {_header_col} !important;
    }}
    .step-num {{
        color: {_header_col} !important;
        -webkit-text-fill-color: {_header_col} !important;
        opacity: 0.22;
    }}
    @media (max-width: 900px) {{
        .steps-grid {{ grid-template-columns: repeat(2, 1fr); }}
        .usecase-grid {{ grid-template-columns: 1fr; }}
        .glossary-grid {{ grid-template-columns: 1fr; }}
        .hero-sun-bg {{ display: none; }}
    }}
    </style>

    <div class="hero-wrap">
        <div class="hero-sun-bg">☀️</div>
        <div class="hero-eyebrow">Sun Scout · Solar Intelligence</div>
        <div class="hero-title">Know Your <span>Sunlight</span><br>Before You Buy.</div>
        <div class="hero-sub">
            The tool built for one question every house hunter should ask —
            <em>when does sunlight actually hit that balcony?</em>
        </div>
    </div>

    <div class="section-label">How to use</div>
    <div class="steps-grid">
        <div class="step-card">
            <div class="step-num">01</div>
            <span class="step-icon">📍</span>
            <div class="step-title">Pin Your Location</div>
            <div class="step-body">Search an address in the sidebar or click anywhere on the 2D map. Drop your pin on the property you're evaluating.</div>
            <div class="step-arrow">›</div>
        </div>
        <div class="step-card">
            <div class="step-num">02</div>
            <span class="step-icon">🗓️</span>
            <div class="step-title">Pick a Date & Time</div>
            <div class="step-body">Use the sidebar sliders or choose a celestial preset — Summer Solstice, Winter Solstice, or any date in between.</div>
            <div class="step-arrow">›</div>
        </div>
        <div class="step-card">
            <div class="step-num">03</div>
            <span class="step-icon">🛰️</span>
            <div class="step-title">Choose Your View</div>
            <div class="step-body">Switch between 2D map, 3D Arc, or 3D Shadow views in the Explorer tab. Hit Play to animate the sun path.</div>
            <div class="step-arrow">›</div>
        </div>
        <div class="step-card">
            <div class="step-num">04</div>
            <span class="step-icon">🔄</span>
            <div class="step-title">Compare Seasons</div>
            <div class="step-body">Scroll down in Explorer to see all four seasonal sun paths overlaid on the same map for year-round comparison.</div>
        </div>
    </div>

    <div class="section-label">Who is this for</div>
    <div class="usecase-grid">
        <div class="usecase-card">
            <div class="usecase-icon">🏡</div>
            <div>
                <div class="usecase-title">House Hunters</div>
                <div class="usecase-body">
                    That "sunny south-facing balcony" might be shaded by the 8-storey building next door from October to March.
                    Check it before you sign.
                </div>
                <div class="usecase-tag">Core use case</div>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">🌿</div>
            <div>
                <div class="usecase-title">Gardeners</div>
                <div class="usecase-body">
                    Full-sun plants need 6+ hours of direct light. Use the Play Path animation to watch sunlight move across your garden hour by hour.
                </div>
                <div class="usecase-tag">Planting decisions</div>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">⚡</div>
            <div>
                <div class="usecase-title">Solar Panel Owners</div>
                <div class="usecase-body">
                    Check peak solar radiation hours by season and see if your roof gets the minimum needed for viable solar generation.
                </div>
                <div class="usecase-tag">Energy planning</div>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">📸</div>
            <div>
                <div class="usecase-title">Photographers</div>
                <div class="usecase-body">
                    Use the 3D Arc view to find the exact azimuth and elevation of the sun at your shoot location — down to the minute.
                </div>
                <div class="usecase-tag">Shot planning</div>
            </div>
        </div>
    </div>

    <div class="section-label">Understanding the numbers</div>
    <div class="glossary-grid">
        <div class="glossary-item">
            <div class="glossary-key">Azimuth</div>
            <div class="glossary-val">Compass direction of the sun. North = 0°, East = 90°, South = 180°, West = 270°.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Elevation</div>
            <div class="glossary-val">How high the sun is above the horizon. 0° = just risen or setting. 90° = directly overhead.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Solar Noon</div>
            <div class="glossary-val">The moment the sun peaks for the day — highest elevation, shortest shadows.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Radiation W/m²</div>
            <div class="glossary-val">Estimated sunlight intensity. Above 600 W/m² is strong solar generation territory.</div>
        </div>
    </div>

    <div style="margin-top:24px;padding:16px 20px;
         background:{_card_bg};border:1px solid {_card_border};
         border-radius:12px;display:flex;gap:14px;align-items:center;">
        <div style="font-size:22px;flex-shrink:0;">🔬</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.82rem;
             color:{'#374151' if _is_light else '#E2E8F0'};line-height:1.6;">
            Sun Scout uses the <b style="color:{_header_col};">Astral</b> library for
            precise astronomical calculations, <b style="color:{_header_col};">OpenStreetMap</b>
            for building geometry, and the <b style="color:{_header_col};">Overpass API</b>
            for real building heights. Solar positions are accurate to within fractions of a degree.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXPLORER (location + visualisation + year-round, all in one)
# ══════════════════════════════════════════════════════════════════════════════
with tab_explorer:
    st.markdown(_INFO_CARD_CSS, unsafe_allow_html=True)

    # ── Top controls row ──────────────────────────────────────────────────────
    view_mode = st.radio(
        "Select View",
        ["📍 Location Setup", "▶ Live", "🔄 Year Summary"],
        horizontal=True, key="view_mode"
    )
    animate_trigger = True  # always on for live views

    # ── Build path data ───────────────────────────────────────────────────────
    path_data = build_path_data()

    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(
        city_info, sim_time, radius_meters, lat, lon)

    if m_el <= 0:
        st.warning(f"🌅 The sun is currently below the horizon ({m_el:.1f}°).")

    # ── VIEW BRANCHES ────────────────────────────────────────────────────────────
    if view_mode == "📍 Location Setup":
        # 2D folium map — click to place pin, no animation
        map_key = f"map_setup_{target_date}_{lat}_{lon}"
        m = folium.Map(location=st.session_state.coords, zoom_start=17, tiles=None)
        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri', name='Satellite').add_to(m)
        folium.TileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='&copy; OpenStreetMap contributors', name='Street').add_to(m)
        folium.LayerControl(position='topleft', collapsed=False).add_to(m)
        folium.Marker(
            st.session_state.coords,
            icon=folium.Icon(color='orange', icon='sun', prefix='fa'),
            tooltip=f"{lat:.5f}, {lon:.5f}"
        ).add_to(m)
        info_html = f'''
            <div style="position:absolute;top:10px;right:10px;width:200px;
                        background:rgba(14,17,23,0.92);padding:14px;border-radius:12px;
                        border:2px solid #F39C12;color:white;z-index:1000;pointer-events:none;
                        font-family:JetBrains Mono,monospace;font-size:12px;">
                <div style="color:#F39C12;font-weight:bold;font-size:10px;
                     letter-spacing:1px;margin-bottom:6px;">📍 CLICK MAP TO SET LOCATION</div>
                <div style="color:#9CA3AF;margin-bottom:4px;">Lat: <b style="color:#fff;">{lat:.5f}</b></div>
                <div style="color:#9CA3AF;">Lon: <b style="color:#fff;">{lon:.5f}</b></div>
            </div>'''
        m.get_root().html.add_child(folium.Element(info_html))
        map_data = st_folium(m, height=550, use_container_width=True, key=map_key)
        if map_data and map_data.get("last_clicked"):
            new_coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
            if new_coords != st.session_state.coords:
                st.session_state.coords = new_coords
                st.rerun()
        st.info("💡 Click anywhere on the map to set your location, then switch to **2D Live** or **3D Live** to visualize.")

    elif view_mode == "▶ Live":
        rise_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, rise_t), radius_meters)
        set_edge  = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, set_t),  radius_meters)
        animate_trigger = st.toggle("▶ Play Path", value=True, key="anim_toggle_live")
        visuals.render_live_component(
            lat, lon, radius_meters, path_data, animate_trigger, sim_time,
            m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
            rise_edge, set_edge,
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"),
            env_data["aqi"] if enable_aqi else "Off",
            init_rot=st.session_state["cam3d_rot"],
            init_tilt=st.session_state["cam3d_tilt"],
            init_zoom=st.session_state["cam3d_zoom"],
        )

    else:  # Year Summary
        st.markdown(f"""
        <div style="background:{_card_bg};border:1px solid {_card_border};
             border-radius:12px;padding:16px 22px;margin-bottom:12px;">
            <span style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;
                 letter-spacing:2px;color:{_header_col};">🔄 Seasonal Sun Path Comparison</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                 color:{_sub_col};margin-left:14px;">All four seasons overlaid</span>
        </div>
        """, unsafe_allow_html=True)
        milestones = [
            {"id": "Summer", "label": "Summer (June 21)",  "date": date(2026, 6, 21)},
            {"id": "Autumn", "label": "Autumn (Oct 31)",   "date": date(2026, 10, 31)},
            {"id": "Spring", "label": "Spring (March 20)", "date": date(2026, 3, 20)},
            {"id": "Winter", "label": "Winter (Dec 21)",   "date": date(2026, 12, 21)},
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
            seasonal_data[ms["id"]] = {"coords": pts, "label": ms["label"]}
        visuals.render_seasonal_map(lat, lon, radius_meters, seasonal_data)
        _legend_bg = "rgba(255,255,255,0.7)" if _is_light else "rgba(255,255,255,0.05)"
        st.markdown(f"""
        <div style="display:flex;justify-content:space-around;background:{_legend_bg};
             padding:12px;border-radius:10px;margin-top:10px;border:1px solid {_card_border};">
            <div style="font-family:'JetBrains Mono',monospace;font-size:13px;display:flex;align-items:center;gap:6px;">
                <span style="display:inline-block;width:18px;height:3px;background:#FF4444;border-radius:2px;"></span>
                <span style="color:#FF4444 !important;-webkit-text-fill-color:#FF4444 !important;">Summer</span>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:13px;display:flex;align-items:center;gap:6px;">
                <span style="display:inline-block;width:18px;height:3px;background:#FF8C00;border-radius:2px;"></span>
                <span style="color:#FF8C00 !important;-webkit-text-fill-color:#FF8C00 !important;">Autumn</span>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:13px;display:flex;align-items:center;gap:6px;">
                <span style="display:inline-block;width:18px;height:3px;background:#C8A800;border-radius:2px;"></span>
                <span style="color:#C8A800 !important;-webkit-text-fill-color:#C8A800 !important;">Spring</span>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:13px;display:flex;align-items:center;gap:6px;">
                <span style="display:inline-block;width:18px;height:3px;background:#5BAED8;border-radius:2px;"></span>
                <span style="color:#5BAED8 !important;-webkit-text-fill-color:#5BAED8 !important;">Winter</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Metrics & elevation chart ─────────────────────────────────────────────
    render_metrics_and_chart("explorer")
