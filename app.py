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

# ── THEME STATE (must init before apply_styles) ───────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

visuals.apply_styles(st.session_state.theme)

# ── GPS / SESSION STATE INIT ──────────────────────────────────────────────────
if 'coords' not in st.session_state:
    st.session_state.coords         = [0.0, 0.0]
    st.session_state.gps_requested  = False

# Camera persistence — read URL query params FIRST, before any widget renders.
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

# ── Resolve theme-aware colours for inline use ────────────────────────────────
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
        /* Theme pill buttons */
        .theme-pill {{
            display: inline-flex; align-items: center; justify-content: center;
            gap: 5px; padding: 7px 0; border-radius: 10px; cursor: pointer;
            font-size: 12px; font-weight: 600; font-family: 'Inter', sans-serif;
            transition: all .2s; width: 100%; border: none; letter-spacing: .04em;
        }}
        .theme-pill-dark {{
            background: {"rgba(243,156,18,0.12)" if not _is_light else "rgba(0,0,0,0.05)"};
            color: {"#F39C12" if not _is_light else "#777"};
            border: 1px solid {"rgba(243,156,18,.3)" if not _is_light else "rgba(0,0,0,.08)"} !important;
        }}
        .theme-pill-light {{
            background: {"rgba(0,0,0,0.05)" if not _is_light else "rgba(212,134,10,0.12)"};
            color: {"#777" if not _is_light else "#C47A0C"};
            border: 1px solid {"rgba(0,0,0,.08)" if not _is_light else "rgba(212,134,10,.3)"} !important;
        }}
        </style>

        <h1 class="flowstate-title">SUN<br>SCOUT</h1>
        <p class="flowstate-subtitle">Visualize the Light</p>
    """, unsafe_allow_html=True)

    # ── Theme toggle ──────────────────────────────────────────────────────────
    st.markdown(f"""
        <div style="margin-bottom:6px;font-size:9px;letter-spacing:.14em;
             text-transform:uppercase;color:{_sub_col};
             font-family:'JetBrains Mono',monospace;">
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


# ── DASHBOARD FOOTER ──────────────────────────────────────────────────────────
def render_dashboard_footer(key_suffix):
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


# ── HELPER: build path_data list ──────────────────────────────────────────────
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


# ── INFO CARD STYLES (theme-aware) ────────────────────────────────────────────
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
    .use-case-item {{ margin-bottom: 15px; line-height: 1.6; color: {_body_col}; }}
    .info-card p {{ color: {_body_col} !important; }}
    .info-card li {{ color: {_body_col} !important; }}
    .info-card td {{ color: {_body_col} !important; }}
    td[style*="color: #F39C12"] {{ color: {_header_col} !important; }}
    td[style*="color: #9CA3AF"] {{ color: {_sub_col} !important; }}
</style>
"""

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_info, tab1, tab2, tab_summary, tab_balcony = st.tabs([
    "Getting Started",
    "Step 1: 📍 Location Setup",
    "Step 2: 🚀 Live Visualization",
    "🔄 Year Round Summary",
    "🏠 Balcony Report",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — INFO & HELP
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown(_INFO_CARD_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Hero ── */
    .hero-wrap {{
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 28px;
        background: linear-gradient(135deg, #0D0F14 0%, #141820 60%, #1a1408 100%);
        border: 1px solid rgba(243,156,18,0.15);
        padding: 52px 48px 48px;
    }}
    .hero-wrap::before {{
        content: '';
        position: absolute; inset: 0;
        background:
            radial-gradient(ellipse 70% 60% at 80% 50%, rgba(243,156,18,0.07) 0%, transparent 70%),
            radial-gradient(ellipse 40% 40% at 20% 80%, rgba(243,156,18,0.04) 0%, transparent 60%);
        pointer-events: none;
    }}
    .hero-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px; letter-spacing: .22em; text-transform: uppercase;
        color: {_header_col}; margin-bottom: 14px; opacity: 0.85;
    }}
    .hero-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(2.8rem, 5vw, 4.4rem);
        letter-spacing: 3px; line-height: 1.0;
        color: #F0F2F5; margin-bottom: 6px;
    }}
    .hero-title span {{ color: {_header_col}; }}
    .hero-sub {{
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem; font-weight: 300;
        color: {'#4B5563' if _is_light else '#6B7280'};
        margin-bottom: 32px; max-width: 520px; line-height: 1.7;
    }}
    .hero-story {{
        background: rgba(243,156,18,0.06);
        border: 1px solid rgba(243,156,18,0.18);
        border-left: 4px solid {_header_col};
        border-radius: 12px;
        padding: 18px 22px;
        max-width: 600px;
        font-family: 'Inter', sans-serif;
        font-size: 0.92rem;
        color: {'#374151' if _is_light else '#9CA3AF'};
        line-height: 1.75;
        font-style: italic;
    }}
    .hero-story b {{ color: {_header_col}; font-style: normal; font-weight: 600; }}
    .hero-sun-bg {{
        position: absolute; right: 48px; top: 50%;
        transform: translateY(-50%);
        font-size: 130px; line-height: 1;
        opacity: 0.12; pointer-events: none;
        filter: blur(2px);
        user-select: none;
    }}

    /* ── How-to steps ── */
    .steps-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 28px;
    }}
    .step-card {{
        background: {_card_bg};
        border: 1px solid {_card_border};
        border-radius: 14px;
        padding: 22px 18px;
        position: relative;
        transition: transform .15s;
    }}
    .step-num {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3rem; letter-spacing: 2px;
        color: {_header_col}; opacity: 0.22;
        line-height: 1; margin-bottom: 8px;
    }}
    .step-icon {{ font-size: 26px; margin-bottom: 10px; display: block; }}
    .step-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.1rem; letter-spacing: 1.5px;
        color: {_header_col}; margin-bottom: 8px;
        text-transform: uppercase;
    }}
    .step-body {{
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem; line-height: 1.6;
        color: {'#4B5563' if _is_light else '#6B7280'};
    }}
    .step-arrow {{
        position: absolute; top: 50%; right: -10px;
        transform: translateY(-50%);
        font-size: 18px; color: {_header_col}; opacity: 0.35;
        z-index: 2;
    }}

    /* ── Use case cards ── */
    .usecase-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 14px;
        margin-bottom: 28px;
    }}
    .usecase-card {{
        background: {_card_bg};
        border: 1px solid {_card_border};
        border-radius: 14px;
        padding: 22px 22px;
        display: flex; gap: 16px; align-items: flex-start;
    }}
    .usecase-icon {{
        font-size: 32px; flex-shrink: 0;
        width: 52px; height: 52px;
        background: rgba(243,156,18,0.08);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid rgba(243,156,18,0.15);
    }}
    .usecase-title {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.1rem; letter-spacing: 1.5px;
        color: {_header_col}; margin-bottom: 6px;
        text-transform: uppercase;
    }}
    .usecase-body {{
        font-family: 'Inter', sans-serif;
        font-size: 0.83rem; line-height: 1.65;
        color: {'#4B5563' if _is_light else '#6B7280'};
    }}
    .usecase-tag {{
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 9px; letter-spacing: .12em;
        text-transform: uppercase;
        background: rgba(243,156,18,0.1);
        color: {_header_col};
        border: 1px solid rgba(243,156,18,0.2);
        border-radius: 20px; padding: 2px 10px;
        margin-top: 8px; display: inline-block;
    }}

    /* ── Feature pills ── */
    .feature-row {{
        display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 28px;
    }}
    .feature-pill {{
        background: {_card_bg};
        border: 1px solid {_card_border};
        border-radius: 30px;
        padding: 8px 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px; color: {'#374151' if _is_light else '#9CA3AF'};
        display: flex; align-items: center; gap: 7px;
    }}
    .feature-pill span {{ color: {_header_col}; font-size: 14px; }}

    /* ── Glossary ── */
    .glossary-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 0;
    }}
    .glossary-item {{
        background: {_card_bg};
        border: 1px solid {_card_border};
        border-radius: 12px; padding: 16px 18px;
        display: flex; gap: 12px; align-items: flex-start;
    }}
    .glossary-key {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1rem; letter-spacing: 1px;
        color: {_header_col}; white-space: nowrap;
        min-width: 90px;
    }}
    .glossary-val {{
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem; line-height: 1.55;
        color: {'#4B5563' if _is_light else '#6B7280'};
    }}

    /* ── Section label ── */
    .section-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 9px; letter-spacing: .22em;
        text-transform: uppercase;
        color: {_header_col}; opacity: 0.7;
        margin-bottom: 12px; margin-top: 4px;
    }}

    @media (max-width: 900px) {{
        .steps-grid {{ grid-template-columns: repeat(2, 1fr); }}
        .usecase-grid {{ grid-template-columns: 1fr; }}
        .glossary-grid {{ grid-template-columns: 1fr; }}
        .hero-sun-bg {{ display: none; }}
    }}
    </style>

    <!-- ── HERO ─────────────────────────────────────────────── -->
    <div class="hero-wrap">
        <div class="hero-sun-bg">☀️</div>
        <div class="hero-eyebrow">Sun Scout · Solar Intelligence</div>
        <div class="hero-title">Know Your <span>Sunlight</span><br>Before You Buy.</div>
        <div class="hero-sub">
            The tool built for one question every house hunter should ask —
            <em>when does sunlight actually hit that balcony?</em>
        </div>
    </div>

    <!-- ── HOW TO USE ────────────────────────────────────────── -->
    <div class="section-label">How to use</div>
    <div class="steps-grid">
        <div class="step-card">
            <div class="step-num">01</div>
            <span class="step-icon">📍</span>
            <div class="step-title">Pin Your Location</div>
            <div class="step-body">Search an address or click anywhere on the 2D map in Step 1. Drop your pin exactly on the property you're evaluating.</div>
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
            <div class="step-title">Watch the Shadow</div>
            <div class="step-body">Switch to Step 2 → 3D Shadow view. Hit Play and watch the sun move across real buildings in real time.</div>
            <div class="step-arrow">›</div>
        </div>
        <div class="step-card">
            <div class="step-num">04</div>
            <span class="step-icon">🏠</span>
            <div class="step-title">Get the Verdict</div>
            <div class="step-body">Open the Balcony Report tab. Set your floor and which way it faces. Get a season-by-season sunlight breakdown in minutes.</div>
        </div>
    </div>

    <!-- ── USE CASES ─────────────────────────────────────────── -->
    <div class="section-label">Who is this for</div>
    <div class="usecase-grid">
        <div class="usecase-card">
            <div class="usecase-icon">🏡</div>
            <div>
                <div class="usecase-title">House Hunters</div>
                <div class="usecase-body">
                    That "sunny south-facing balcony" might be shaded by the 8-storey building next door from October to March.
                    Check it before you sign. Set your floor, set the surrounding building height, and see exactly what you're buying.
                </div>
                <div class="usecase-tag">Core use case</div>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">🌿</div>
            <div>
                <div class="usecase-title">Gardeners</div>
                <div class="usecase-body">
                    Full-sun plants need 6+ hours of direct light. Use the Play Path animation to watch sunlight move across your garden plot hour by hour. Know before you plant.
                </div>
                <div class="usecase-tag">Planting decisions</div>
            </div>
        </div>
        <div class="usecase-card">
            <div class="usecase-icon">⚡</div>
            <div>
                <div class="usecase-title">Solar Panel Owners</div>
                <div class="usecase-body">
                    Is that neighbour's new extension going to shade your roof in winter?
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
                    Golden hour is just 20–30 minutes. Use the 3D Arc view to find the exact azimuth and elevation of the sun at your shoot location — down to the minute.
                </div>
                <div class="usecase-tag">Shot planning</div>
            </div>
        </div>
    </div>

    <!-- ── FEATURES ──────────────────────────────────────────── -->
    <div class="section-label">What's inside</div>
    <div class="feature-row">
        <div class="feature-pill"><span>🗺️</span> 2D Street & Satellite Map</div>
        <div class="feature-pill"><span>🌐</span> 3D Sun Arc (Three.js)</div>
        <div class="feature-pill"><span>🛰️</span> 3D Building Shadows (OSM)</div>
        <div class="feature-pill"><span>🏠</span> Balcony Report by Season</div>
        <div class="feature-pill"><span>🧭</span> Facing Direction Filter</div>
        <div class="feature-pill"><span>🏢</span> Floor-by-Floor Analysis</div>
        <div class="feature-pill"><span>🔄</span> Year-Round Arc Comparison</div>
        <div class="feature-pill"><span>⚡</span> Live AQI & Weather</div>
        <div class="feature-pill"><span>📍</span> GPS Auto-Location</div>
        <div class="feature-pill"><span>🌙</span> Dark / Light Mode</div>
        <div class="feature-pill"><span>📅</span> Solstice & Equinox Presets</div>
        <div class="feature-pill"><span>☀️</span> Solar Radiation (W/m²)</div>
    </div>

    <!-- ── GLOSSARY ───────────────────────────────────────────── -->
    <div class="section-label">Understanding the numbers</div>
    <div class="glossary-grid">
        <div class="glossary-item">
            <div class="glossary-key">Azimuth</div>
            <div class="glossary-val">Compass direction of the sun. North = 0°, East = 90°, South = 180°, West = 270°. Tells you which side of the building the sun is on.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Elevation</div>
            <div class="glossary-val">How high the sun is above the horizon. 0° = just risen or setting. 90° = directly overhead. Low elevation = long shadows.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Solar Noon</div>
            <div class="glossary-val">The moment the sun peaks for the day — highest elevation, shortest shadows. Not always 12:00; depends on your longitude and timezone offset.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Obstruction °</div>
            <div class="glossary-val">The minimum solar elevation needed to clear a nearby building. If the building angle is 32° and the sun is at 28°, you're in shadow.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Radiation W/m²</div>
            <div class="glossary-val">Estimated sunlight intensity hitting a flat surface. Above 600 W/m² is strong solar generation territory. Below 200 W/m² is marginal.</div>
        </div>
        <div class="glossary-item">
            <div class="glossary-key">Facing Arc</div>
            <div class="glossary-val">A south-facing balcony can "see" the sun when it's within ±90° of south (i.e., between east and west). North-facing misses most direct sun.</div>
        </div>
    </div>

    <!-- ── FOOTER NOTE ────────────────────────────────────────── -->
    <div style="margin-top:24px;padding:16px 20px;
         background:{_card_bg};border:1px solid {_card_border};
         border-radius:12px;display:flex;gap:14px;align-items:center;">
        <div style="font-size:22px;flex-shrink:0;">🔬</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.82rem;
             color:{'#4B5563' if _is_light else '#6B7280'};line-height:1.6;">
            Sun Scout uses the <b style="color:{_header_col};">Astral</b> library for
            precise astronomical calculations, <b style="color:{_header_col};">OpenStreetMap</b>
            for building geometry, and the <b style="color:{_header_col};">Overpass API</b>
            for real building heights. Solar positions are accurate to within fractions of a degree.
            Building obstruction is a geometric model — trees, fences, and unmapped structures
            won't appear.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LOCATION SETUP
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    display_lat  = f"{st.session_state.coords[0]:.5f}"
    display_lon  = f"{st.session_state.coords[1]:.5f}"
    display_date = target_date.strftime("%B %d, %Y")
    map_key      = f"map_select_{target_date}_{st.session_state.coords[0]}"

    st.markdown(_INFO_CARD_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-card">
        <div class="info-sub">What to do here?</div>
        <p>Select your location on the 2D Map. Also select the date and time. View your location on the 3D map. Then switch the "Step 2" to see the sun path, and the shadows.</p>
    </div>
    """, unsafe_allow_html=True)

    loc_view = st.radio("Map Style", ["🗺️ 2D Map", "🏙️ 3D Buildings"],
                        horizontal=True, key="loc_map_style")

    if loc_view == "🏙️ 3D Buildings":
        _path_data = build_path_data()
        _m_slat, _m_slon, _m_shlat, _m_shlon, _m_az, _m_el = solarlogic.get_solar_pos(
            city_info, sim_time, radius_meters, lat, lon)

        st.components.v1.html("""
        <script>
        window.addEventListener('message', function(e) {
            if (!e.data || e.data.type !== 'osm_pin') return;
            const url = new URL(window.parent.location.href);
            url.searchParams.set('pin_lat', e.data.lat.toFixed(6));
            url.searchParams.set('pin_lon', e.data.lon.toFixed(6));
            window.parent.history.replaceState({}, '', url.toString());
        });
        </script>
        """, height=0)

        visuals.render_3d_shadow_component(
            lat, lon, radius_meters, _path_data,
            False,
            sim_time,
            _m_slat, _m_slon, _m_shlat, _m_shlon, _m_el, _m_az,
            rise_t.strftime("%H:%M"),
            set_t.strftime("%H:%M"),
            allow_location_select=True,
            init_rot=st.session_state["cam3d_rot"],
            init_tilt=st.session_state["cam3d_tilt"],
            init_zoom=st.session_state["cam3d_zoom"],
        )

        qp = st.query_params
        if "pin_lat" in qp and "pin_lon" in qp:
            try:
                new_pin = [float(qp["pin_lat"]), float(qp["pin_lon"])]
                if new_pin != st.session_state.coords:
                    st.session_state.coords = new_pin
                    st.query_params.clear()
                    st.rerun()
            except (ValueError, TypeError):
                pass

        st.info("View your location on the 3d map.")

    else:
        m = folium.Map(location=st.session_state.coords, zoom_start=17, tiles=None)
        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri', name='Satellite').add_to(m)
        folium.TileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='&copy; OpenStreetMap contributors', name='Street').add_to(m)
        folium.LayerControl(position='topleft', collapsed=False).add_to(m)
        folium.Marker(st.session_state.coords,
                      icon=folium.Icon(color='orange', icon='sun', prefix='fa')).add_to(m)

        info_html = f'''
            <div style="position:absolute;top:10px;right:10px;width:180px;
                        background:rgba(14,17,23,0.9);padding:12px;border-radius:10px;
                        border:2px solid #F39C12;color:white;
                        font-family:'Inter',sans-serif;font-size:13px;
                        z-index:1000;pointer-events:none;">
                <div style="color:#F39C12;font-weight:bold;font-size:11px;letter-spacing:1px;">📍 LOCATION</div>
                <div style="margin-bottom:8px;">{display_lat}, {display_lon}</div>
                <div style="color:#F39C12;font-weight:bold;font-size:11px;letter-spacing:1px;">📅 SELECTED DATE</div>
                <div>{display_date}</div>
            </div>'''
        m.get_root().html.add_child(folium.Element(info_html))

        map_data = st_folium(m, height=550, use_container_width=True, key=map_key)
        if map_data and map_data.get("last_clicked"):
            new_coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
            if new_coords != st.session_state.coords:
                st.session_state.coords = new_coords
                st.rerun()

    render_dashboard_footer("location")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LIVE VISUALISATION
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    ctrl_col1, ctrl_col2 = st.columns([1, 1])
    with ctrl_col1:
        animate_trigger = st.toggle("Play Path", value=True, key="anim_toggle")
    with ctrl_col2:
        view_mode = st.radio("Map View",
                             ["🗺️ Street/Satellite", "🌐 3D Arc", "🛰️ 3D Shadow"],
                             horizontal=True, key="view_mode")

    st.markdown("For selected date and time.")

    path_data = build_path_data()

    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(
        city_info, sim_time, radius_meters, lat, lon)

    if m_el <= 0:
        st.warning(f"🌅 The sun is currently below the horizon ({m_el:.1f}°).")

    rise_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, rise_t), radius_meters)
    set_edge  = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, set_t),  radius_meters)

    if view_mode == "🌐 3D Arc":
        visuals.render_3d_map_component(
            lat, lon, radius_meters, path_data, animate_trigger, sim_time,
            m_slat, m_slon, m_el,
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"),
            init_rot=st.session_state["cam3d_rot"],
            init_tilt=st.session_state["cam3d_tilt"],
            init_zoom=st.session_state["cam3d_zoom"],
        )

    elif view_mode == "🛰️ 3D Shadow":
        visuals.render_3d_shadow_component(
            lat, lon, radius_meters, path_data, animate_trigger, sim_time,
            m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"),
            init_rot=st.session_state["cam3d_rot"],
            init_tilt=st.session_state["cam3d_tilt"],
            init_zoom=st.session_state["cam3d_zoom"],
        )

    else:
        visuals.render_map_component(
            lat, lon, radius_meters, path_data, animate_trigger, sim_time,
            m_slat, m_slon, m_shlat, m_shlon, m_el,
            rise_edge, set_edge,
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"),
            env_data["aqi"] if enable_aqi else "Off")

    render_dashboard_footer("visualisation")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — YEAR ROUND SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with tab_summary:
    st.markdown(f'<div style="background:{_card_bg};border:1px solid {_card_border};'
                f'border-radius:12px;padding:20px 25px;margin-bottom:20px;">'
                f'<h2 style="font-family:\'Bebas Neue\',sans-serif;color:{_header_col};'
                f'letter-spacing:2px;margin:0;">Seasonal Comparison For Selected Location</h2>'
                f'</div>', unsafe_allow_html=True)

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
    <div style="display:flex; justify-content:space-around; background:{_legend_bg};
         padding:15px; border-radius:10px; margin-top:10px;
         border:1px solid {_card_border};">
        <div style="color:#FF4444;font-family:'JetBrains Mono',monospace;font-size:13px;">&#9679; Summer</div>
        <div style="color:#FF8C00;font-family:'JetBrains Mono',monospace;font-size:13px;">&#9679; Autumn</div>
        <div style="color:#C8A800;font-family:'JetBrains Mono',monospace;font-size:13px;">&#9679; Spring</div>
        <div style="color:#5BAED8;font-family:'JetBrains Mono',monospace;font-size:13px;">&#9679; Winter</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BALCONY REPORT  (building-obstruction aware)
# ══════════════════════════════════════════════════════════════════════════════
with tab_balcony:
    st.markdown(_INFO_CARD_CSS, unsafe_allow_html=True)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def fmt_duration(minutes):
        if minutes <= 0:
            return "No direct sun"
        h, m = minutes // 60, minutes % 60
        return f"{h}h {m:02d}min" if h else f"{m} min"

    def sunlight_bar_html(hourly, color):
        cells = ""
        for pt in hourly:
            fill = color if pt["lit"] else (
                "rgba(255,255,255,0.06)" if not _is_light else "rgba(0,0,0,0.06)")
            tip = (f"{pt['hour']:02d}:30 \u2014 sun visible" if pt["lit"]
                   else f"{pt['hour']:02d}:30 \u2014 blocked (need >{pt['needed_el']}\xb0)")
            cells += (f'<div title="{tip}" style="flex:1;height:28px;'
                      f'background:{fill};border-radius:3px;margin:0 1px;"></div>')
        labels = "".join(
            f'<div style="flex:1;text-align:center;font-size:8px;color:{_sub_col};'
            f'font-family:JetBrains Mono,monospace;">'
            f'{str(6 + i) if i % 2 == 0 else ""}</div>'
            for i in range(15))
        return (f'<div style="display:flex;gap:0;margin-bottom:3px;">{cells}</div>'
                f'<div style="display:flex;gap:0;">{labels}</div>')

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="info-card" style="border-left:4px solid {_header_col};">
        <div class="info-header">\U0001f3e0 Balcony Sunlight Report</div>
        <div class="info-sub">Real sunlight \u2014 floor & buildings aware</div>
        <p>Set your floor and surrounding building height.
        We calculate exactly when sunlight hits across all four seasons.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Controls row ──────────────────────────────────────────────────────────
    ctrl1, ctrl2 = st.columns(2)

    with ctrl1:
        floor_num = int(st.number_input(
            "\U0001f3e2 Your Floor (0=Ground, max 35)",
            min_value=0, max_value=35, value=0, step=1,
            key="balcony_floor_v2"))
        floor_m = solarlogic.floor_elevation_m(floor_num)
        if floor_num == 0:   selected_floor_label = "Ground Floor"
        elif floor_num == 1: selected_floor_label = "1st Floor"
        elif floor_num == 2: selected_floor_label = "2nd Floor"
        elif floor_num == 3: selected_floor_label = "3rd Floor"
        else:                selected_floor_label = f"{floor_num}th Floor"

    with ctrl2:
        surround_floors = st.slider(
            "\U0001f3d9\ufe0f Surrounding buildings (floors)",
            min_value=0, max_value=35, value=3, step=1,
            key="surround_height",
            help="How tall are the buildings immediately around you? "
                 "0=open field, 3=low-rise, 10=mid-rise, 20+=high-rise.")
        surround_h = solarlogic.floor_elevation_m(surround_floors)
        surround_label = ("open field" if surround_floors == 0
                          else f"{surround_floors}-floor (~{surround_h:.0f}m)")

    # ── Fetch / build obstruction model ──────────────────────────────────────
    with st.spinner("Fetching nearby buildings from OpenStreetMap..."):
        osm_buildings, osm_ok = solarlogic.fetch_nearby_buildings(lat, lon, radius_m=200)

    buildings = solarlogic.make_synthetic_buildings(
        surround_height_m=surround_h, surround_dist_m=20)

    # Status line
    if osm_ok and osm_buildings:
        osm_note = (f"\u2705 OSM: {len(osm_buildings)} buildings found nearby \u2014 "
                    f"slider overrides for manual scenario testing.")
    elif osm_ok:
        osm_note = "\u2705 OSM reachable \u2014 no buildings within 200m (open area)."
    else:
        osm_note = "\u26a0\ufe0f OSM unreachable \u2014 using slider model only."

    st.markdown(f"""
    <div style="background:{_card_bg};border:1px solid {_card_border};
         border-radius:12px;padding:14px 20px;margin:10px 0 16px;
         display:flex;flex-wrap:wrap;gap:20px;align-items:center;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
             color:{_header_col};">
            \U0001f4cd {lat:.4f}, {lon:.4f}
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{_sub_col};">
            Floor: <b style="color:{_body_col};">{selected_floor_label}</b>
            &nbsp;\u00b7&nbsp; Surroundings: <b style="color:{_body_col};">{surround_label}</b>
        </div>
        <div style="font-size:11px;color:{_sub_col};font-family:'JetBrains Mono',monospace;">
            {osm_note}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Seasons ───────────────────────────────────────────────────────────────
    seasons = [
        {"id": "summer", "label": "Summer",  "emoji": "\u2600\ufe0f",
         "date": date(2026, 6, 21),  "color": "#FF6B35"},
        {"id": "autumn", "label": "Autumn",  "emoji": "\U0001f342",
         "date": date(2026, 10, 31), "color": "#FF8C00"},
        {"id": "spring", "label": "Spring",  "emoji": "\U0001f338",
         "date": date(2026, 3, 20),  "color": "#F39C12"},
        {"id": "winter", "label": "Winter",  "emoji": "\u2744\ufe0f",
         "date": date(2026, 12, 21), "color": "#5BAED8"},
    ]

    with st.spinner("Computing sunlight windows..."):
        results = {}
        for s in seasons:
            results[s["id"]] = solarlogic.compute_sunlight_window(
                city_info, s["date"], local_tz,
                buildings, floor_m,
                radius_meters, lat, lon,
                step_minutes=5,
            )

    # ── Prominent sunlight hours summary ─────────────────────────────────────
    valid    = [s for s in seasons if results[s["id"]]]
    avg_mins = sum(results[s["id"]]["sun_minutes"] for s in valid) // max(len(valid), 1)
    summer_m = results["summer"]["sun_minutes"] if results["summer"] else 0
    winter_m = results["winter"]["sun_minutes"] if results["winter"] else 0

    if   avg_mins >= 300: sum_col, sum_icon = "#27AE60", "\U0001f3c6"
    elif avg_mins >= 180: sum_col, sum_icon = "#F39C12", "\u2705"
    elif avg_mins >= 60:  sum_col, sum_icon = "#E67E22", "\u26a0\ufe0f"
    else:                 sum_col, sum_icon = "#E74C3C", "\U0001f534"

    s_cols = st.columns(3)
    summary_items = [
        ("Avg Daily Sun", fmt_duration(avg_mins), sum_col),
        ("Best (Summer)", fmt_duration(summer_m), "#FF6B35"),
        ("Worst (Winter)", fmt_duration(winter_m), "#5BAED8"),
    ]
    for col, (lbl, val, col_color) in zip(s_cols, summary_items):
        col.markdown(f"""
        <div style="background:{_card_bg};border:1px solid {col_color}44;
             border-radius:14px;padding:18px 16px;text-align:center;
             border-top:3px solid {col_color};">
            <div style="font-size:8px;letter-spacing:.16em;text-transform:uppercase;
                 color:{_sub_col};font-family:'JetBrains Mono',monospace;
                 margin-bottom:8px;">{lbl}</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                 color:{col_color};letter-spacing:2px;line-height:1;">
                {val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:18px 0 6px;'></div>", unsafe_allow_html=True)

    # ── 2x2 season cards ──────────────────────────────────────────────────────
    row1 = st.columns(2)
    row2 = st.columns(2)
    grid = [row1[0], row1[1], row2[0], row2[1]]

    for idx, s in enumerate(seasons):
        r = results[s["id"]]
        with grid[idx]:
            if not r:
                st.markdown(
                    f'<div class="info-card"><b style="color:{s["color"]};">'
                    f'{s["emoji"]} {s["label"]}</b><br>Could not compute.</div>',
                    unsafe_allow_html=True)
                continue

            mins = r["sun_minutes"]
            if   mins >= 360: quality, qcol = "\U0001f7e2 Excellent", "#27AE60"
            elif mins >= 240: quality, qcol = "\U0001f7e1 Good",      "#F39C12"
            elif mins >= 120: quality, qcol = "\U0001f7e0 Moderate",  "#E67E22"
            elif mins > 0:    quality, qcol = "\U0001f534 Limited",   "#E74C3C"
            else:             quality, qcol = "\u26ab No Sun",        "#555555"

            window_str = (f"{r['sun_start']} \u2192 {r['sun_end']}"
                          if r["sun_start"] else "No direct sunlight")
            bar = sunlight_bar_html(r["hourly"], s["color"])

            st.markdown(f"""
            <div style="background:{_card_bg};border:1px solid {s['color']}44;
                 border-radius:14px;padding:20px 22px;margin-bottom:16px;
                 border-top:3px solid {s['color']};">
                <div style="display:flex;justify-content:space-between;
                     align-items:center;margin-bottom:14px;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;
                         letter-spacing:2px;color:{s['color']};">
                        {s['emoji']} {s['label'].upper()}</div>
                    <div style="font-size:11px;font-weight:700;color:{qcol};
                         font-family:'JetBrains Mono',monospace;
                         background:{qcol}18;padding:3px 10px;border-radius:20px;
                         border:1px solid {qcol}44;">{quality}</div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;
                     gap:10px;margin-bottom:14px;">
                    <div style="background:{s['color']}12;border-radius:10px;padding:12px;">
                        <div style="font-size:8px;letter-spacing:.14em;text-transform:uppercase;
                             color:{_sub_col};font-family:'JetBrains Mono',monospace;">
                            Direct Sunlight</div>
                        <div style="font-size:1.4rem;font-family:'Bebas Neue',sans-serif;
                             color:{s['color']};margin-top:2px;letter-spacing:1px;">
                            {fmt_duration(mins)}</div>
                    </div>
                    <div style="background:{s['color']}12;border-radius:10px;padding:12px;">
                        <div style="font-size:8px;letter-spacing:.14em;text-transform:uppercase;
                             color:{_sub_col};font-family:'JetBrains Mono',monospace;">
                            Peak Elevation</div>
                        <div style="font-size:1.4rem;font-family:'Bebas Neue',sans-serif;
                             color:{s['color']};margin-top:2px;letter-spacing:1px;">
                            {r['peak_el']}\xb0</div>
                    </div>
                </div>
                <div style="margin-bottom:8px;">
                    <div style="font-size:9px;letter-spacing:.14em;text-transform:uppercase;
                         color:{_sub_col};font-family:'JetBrains Mono',monospace;
                         margin-bottom:5px;">Sunlight Window</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:13px;
                         font-weight:600;color:{_body_col};">{window_str}</div>
                </div>
                <div style="display:flex;gap:14px;margin-bottom:12px;flex-wrap:wrap;">
                    <span style="font-size:10px;color:{_sub_col};
                         font-family:'JetBrains Mono',monospace;">
                        \U0001f305 <b style="color:{_body_col};">{r['rise']}</b></span>
                    <span style="font-size:10px;color:{_sub_col};
                         font-family:'JetBrains Mono',monospace;">
                        \U0001f31e Noon <b style="color:{_body_col};">{r['noon']}</b></span>
                    <span style="font-size:10px;color:{_sub_col};
                         font-family:'JetBrains Mono',monospace;">
                        \U0001f307 <b style="color:{_body_col};">{r['set']}</b></span>
                    <span style="font-size:10px;color:{_sub_col};
                         font-family:'JetBrains Mono',monospace;">
                        \u2b06\ufe0f Peak <b style="color:{_body_col};">{r['peak_time']}</b></span>
                </div>
                <div style="font-size:8px;letter-spacing:.14em;text-transform:uppercase;
                     color:{_sub_col};font-family:'JetBrains Mono',monospace;
                     margin-bottom:4px;">Hourly 06:00\u201420:00
                     &nbsp;|\u00a0<span style="color:{s['color']};">\u25a0</span> sunlit
                     &nbsp;<span style="color:{_sub_col};">\u25a0</span> blocked</div>
                {bar}
            </div>
            """, unsafe_allow_html=True)

    # ── Season comparison table ───────────────────────────────────────────────
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    rows_html = ""
    for s in seasons:
        r = results[s["id"]]
        if not r:
            continue
        mins = r["sun_minutes"]
        dot = "\U0001f7e2" if mins>=360 else "\U0001f7e1" if mins>=240 else "\U0001f7e0" if mins>=120 else "\U0001f534" if mins>0 else "\u26ab"
        rows_html += f"""
        <tr style="border-bottom:1px solid {_card_border};">
            <td style="padding:11px 8px;font-weight:600;color:{s['color']};
                 font-family:'JetBrains Mono',monospace;">{s['emoji']} {s['label']}</td>
            <td style="padding:11px 8px;text-align:center;color:{_body_col};
                 font-family:'JetBrains Mono',monospace;">{r['rise']}</td>
            <td style="padding:11px 8px;text-align:center;color:{_body_col};
                 font-family:'JetBrains Mono',monospace;font-weight:600;">
                {r['sun_start'] if r['sun_start'] else '\u2014'}</td>
            <td style="padding:11px 8px;text-align:center;color:{_body_col};
                 font-family:'JetBrains Mono',monospace;font-weight:600;">
                {r['sun_end'] if r['sun_end'] else '\u2014'}</td>
            <td style="padding:11px 8px;text-align:center;color:{s['color']};
                 font-family:'Bebas Neue',sans-serif;font-size:1rem;letter-spacing:1px;">
                {fmt_duration(mins)}</td>
            <td style="padding:11px 8px;text-align:center;color:{_body_col};
                 font-family:'JetBrains Mono',monospace;">
                {r['peak_el']}\xb0 @ {r['peak_time']}</td>
            <td style="padding:11px 8px;text-align:center;font-size:16px;">{dot}</td>
        </tr>"""

    def _th(txt):
        return (f'<th style="padding:10px 8px;text-align:center;'
                f'font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                f'letter-spacing:.12em;text-transform:uppercase;color:{_sub_col};">{txt}</th>')

    st.markdown(f"""
    <div style="background:{_card_bg};border:1px solid {_card_border};
         border-radius:14px;padding:22px 26px;margin-bottom:16px;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;
             letter-spacing:2px;color:{_header_col};margin-bottom:4px;">
            \U0001f4ca Season Comparison \u2014 {selected_floor_label}
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:12px;">
            <thead>
                <tr style="border-bottom:2px solid {_card_border};">
                    <th style="padding:10px 8px;text-align:left;
                         font-family:'JetBrains Mono',monospace;font-size:9px;
                         letter-spacing:.12em;text-transform:uppercase;
                         color:{_sub_col};">Season</th>
                    {_th("Sunrise")} {_th("Sun Hits")} {_th("Sun Leaves")}
                    {_th("Total")} {_th("Peak")} {_th("Rating")}
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div style="margin-top:14px;font-size:10px;color:{_sub_col};
             font-family:'JetBrains Mono',monospace;line-height:1.8;">
            \U0001f7e2 Excellent (6h+) &nbsp;\u00b7&nbsp; \U0001f7e1 Good (4\u20136h)
            &nbsp;\u00b7&nbsp; \U0001f7e0 Moderate (2\u20134h)
            &nbsp;\u00b7&nbsp; \U0001f534 Limited (&lt;2h) &nbsp;\u00b7&nbsp; \u26ab None
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Buyer's verdict ───────────────────────────────────────────────────────
    if   avg_mins >= 300: vrd, vcol, vic = "Excellent Sun Exposure",     "#27AE60", "\U0001f3c6"
    elif avg_mins >= 180: vrd, vcol, vic = "Good Sun Exposure",          "#F39C12", "\u2705"
    elif avg_mins >= 60:  vrd, vcol, vic = "Moderate \u2014 Check Winter","#E67E22", "\u26a0\ufe0f"
    else:                 vrd, vcol, vic = "Limited Sun \u2014 Buyer Beware","#E74C3C","\U0001f534"

    if avg_mins >= 300:
        vtxt = ("This balcony gets strong sunlight year-round. Ideal for plants, "
                "solar panels, and morning coffee in any season.")
    elif avg_mins >= 180:
        vtxt = ("Solid sunlight for most of the year. Winter months are shorter on light "
                "but overall this is a well-lit balcony.")
    elif avg_mins >= 60:
        vtxt = (f"Decent in summer ({fmt_duration(summer_m)}) but limited in winter "
                f"({fmt_duration(winter_m)}). Consider a higher floor or check if "
                f"a different facing direction gets more sun.")
    else:
        vtxt = ("Very little direct sunlight. Plants will struggle and it will feel "
                "dim year-round. Try adjusting the floor or facing direction above "
                "to see if this improves.")

    st.markdown(f"""
    <div style="background:{_card_bg};border:1px solid {vcol}44;
         border-radius:14px;padding:22px 26px;margin-bottom:20px;
         border-left:5px solid {vcol};">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            <div style="font-size:28px;">{vic}</div>
            <div>
                <div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;
                     color:{_sub_col};font-family:'JetBrains Mono',monospace;">
                    Buyer's Verdict \u00b7 {selected_floor_label}
                </div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;
                     color:{vcol};letter-spacing:2px;">{vrd}</div>
            </div>
        </div>
        <p style="color:{_body_col};font-size:13px;line-height:1.7;margin:0 0 14px;">
            {vtxt}
        </p>
        <div style="display:flex;gap:24px;flex-wrap:wrap;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{_sub_col};">
                Avg: <b style="color:{vcol};">{fmt_duration(avg_mins)}</b></span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{_sub_col};">
                Best: <b style="color:{vcol};">Summer ({fmt_duration(summer_m)})</b></span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{_sub_col};">
                Worst: <b style="color:{vcol};">Winter ({fmt_duration(winter_m)})</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
