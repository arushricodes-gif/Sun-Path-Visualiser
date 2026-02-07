import streamlit as st
import pytz
import plotly.graph_objects as go
import folium
from datetime import datetime, date, timedelta
from timezonefinder import TimezoneFinder
from astral import LocationInfo
from astral.sun import sunrise, sunset, noon, azimuth
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

import visuals
import solarlogic

st.set_page_config(layout="wide", page_title="Solar Path Visualizer", page_icon="☀️")
visuals.apply_styles()

if 'coords' not in st.session_state:
    st.session_state.coords = [0.0, 0.0] 
    st.session_state.gps_requested = False

if not st.session_state.gps_requested:
    loc = get_geolocation()
    if loc:
        st.session_state.coords = [loc['coords']['latitude'], loc['coords']['longitude']]
        st.session_state.gps_requested = True
        st.rerun()

lat, lon = st.session_state.coords
loc_key = f"{lat}_{lon}"
if "last_loc_key" not in st.session_state or st.session_state.last_loc_key != loc_key:
    st.session_state.env_data = solarlogic.get_environmental_data(lat, lon)
    st.session_state.last_loc_key = loc_key
env_data = st.session_state.env_data

tf = TimezoneFinder()
tz_name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
local_tz = pytz.timezone(tz_name)
city_info = LocationInfo(timezone=tz_name, latitude=lat, longitude=lon)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    with st.form("city_search"):
        search_query = st.text_input("🔍 Search for place", placeholder="e.g. Paris, France")
        if st.form_submit_button("Search") and search_query:
            coords = solarlogic.search_city(search_query)
            if coords: 
                st.session_state.coords = coords
                st.rerun()
    if st.button("📍 Reset to My GPS"):
        st.session_state.gps_requested = False
        st.rerun()
    
    celestial_dates = {"Manual Selection": None, "Spring Equinox (Mar 20)": date(2026, 3, 20), "Summer Solstice (Jun 21)": date(2026, 6, 21), "Autumnal Equinox (Sep 22)": date(2026, 9, 22), "Winter Solstice (Dec 21)": date(2026, 12, 21)}
    date_preset = st.selectbox("Key Celestial Dates", list(celestial_dates.keys()))
    target_date = celestial_dates[date_preset] if date_preset != "Manual Selection" else st.date_input("Select Date", date.today())
    radius_meters = 250
    enable_aqi = st.toggle("AQI and Live Weather\n(Available for live data only)", value=False)
    shour = st.slider("Hour", 0, 23, datetime.now(local_tz).hour)
    smin = st.slider("Minute", 0, 59, 0)
    sim_time = local_tz.localize(datetime.combine(target_date, datetime.min.time())) + timedelta(hours=shour, minutes=smin)

try:
    rise_t = sunrise(city_info.observer, date=target_date, tzinfo=local_tz)
    set_t = sunset(city_info.observer, date=target_date, tzinfo=local_tz)
    noon_t = noon(city_info.observer, date=target_date, tzinfo=local_tz)
except:
    rise_t = sim_time.replace(hour=6, minute=0); set_t = sim_time.replace(hour=18, minute=0); noon_t = sim_time.replace(hour=12, minute=0)

# --- FOOTER RENDERER (PRESERVED) ---
def render_dashboard_footer(key_suffix):
    st.markdown("---")
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(city_info, sim_time, radius_meters, lat, lon)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Selected Time", sim_time.strftime('%H:%M'))
    m_col2.metric("Azimuth", f"{m_az:.1f}°"); m_col3.metric("Elevation", f"{m_el:.1f}°"); m_col4.metric("Solar Noon", noon_t.strftime('%H:%M'))
    if enable_aqi:
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        w_col1.metric("🌡️ Temp", f"{env_data['temp']}°C"); w_col2.metric("💧 Humidity", f"{env_data['hum']}%"); w_col3.metric("🌬️ Wind", f"{env_data['wind']} m/s"); w_col4.metric("💨 AQI", env_data["aqi"], delta=env_data["label"], delta_color="inverse")
    
    path_pts = []
    temp_curr = rise_t
    while temp_curr <= set_t:
        _, _, _, _, _, el = solarlogic.get_solar_pos(city_info, temp_curr, radius_meters, lat, lon)
        path_pts.append({"time": temp_curr.strftime("%H:%M"), "el": el})
        temp_curr += timedelta(minutes=15)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[p['time'] for p in path_pts], y=[p['el'] for p in path_pts], mode='lines', line=dict(color='#f39c12', width=3), fill='tozeroy', fillcolor='rgba(243, 156, 18, 0.1)'))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Elevation (°)"))
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")

# --- MAIN LAYOUT ---
st.markdown('<h1 class="main-title">☀️SOLAR PATH VISUALIZER☀️</h1>', unsafe_allow_html=True)
top_col1, top_col2 = st.columns([2.5, 1])
with top_col1:
    st.markdown(f'<div class="obs-card"><h4 style="color:#F7DF88; margin-top:0;">🗺️Where are you?</h4><p style="color:#ffffff; font-size:0.95rem; line-height:1.6;">Tracking solar trajectory at <b>{lat:.4f}, {lon:.4f}</b>.<br>The <span style="color:#e74c3c; font-weight:bold;">red line</span> is sunrise, <span style="color:#3498db; font-weight:bold;">blue</span> is sunset, <span style="color:#808080; font-weight:bold;">grey</span> is the shadow line.</p></div>', unsafe_allow_html=True)
with top_col2:
    st.markdown(f'<div class="sun-card">🌅 Sunrise: {rise_t.strftime("%H:%M")}<br><br>🌇 Sunset: {set_t.strftime("%H:%M")}<br><br>💨AQI: {env_data["aqi"] if enable_aqi else "Disabled"}</div>', unsafe_allow_html=True)

tab1, tab2, tab_info = st.tabs(["Step 1: 📍 Location Setup", "Step 2: 🚀 Live Visualization", "📖 How it works?"])


with tab1:
    m = folium.Map(location=st.session_state.coords, zoom_start=17)
    st.markdown("Select your location on the map and follow on to step 2.")
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', attr='Esri', name='Satellite').add_to(m)
    folium.TileLayer('openstreetmap', name='Street').add_to(m)
    folium.LayerControl().add_to(m)
    folium.Marker(st.session_state.coords, icon=folium.Icon(color='orange', icon='sun', prefix='fa')).add_to(m)
    map_data = st_folium(m, height=700, use_container_width=True, key="selection_map")
    if map_data and map_data.get("last_clicked"):
        st.session_state.coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        st.rerun()
    render_dashboard_footer("location")

with tab2:
    animate_trigger = st.toggle("🚀 Start Animation", key="anim_toggle")
    path_data = []
    curr = rise_t
    while curr <= set_t:
        slat, slon, shlat, shlon, az, el = solarlogic.get_solar_pos(city_info, curr, radius_meters, lat, lon)
        path_data.append({"lat": slat, "lon": slon, "shlat": shlat, "shlon": shlon, "time": curr.strftime("%H:%M"), "el": el})
        curr += timedelta(minutes=10)
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(city_info, sim_time, radius_meters, lat, lon)
    if m_el <= 0: st.warning(f"🌙 The sun is currently below the horizon ({m_el:.1f}°).")
    
    # Passing edges to visualizer
    rise_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, rise_t), radius_meters)
    set_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, set_t), radius_meters)
    
    visuals.render_map_component(lat, lon, radius_meters, path_data, animate_trigger, sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, rise_edge, set_edge)
    render_dashboard_footer("visualisation")

with tab_info:
    st.markdown("""
        <div class="theory-section">
            <h2 class="theory-header">☀️ About Solar Path Visualizer</h2>
            <p style="color:#ffffff; line-height:1.6;">
                Have you ever wondered about the exact movement of the sun or how much sunlight a specific spot on Earth receives? 
                This tool is designed to showcase the <b>solar trajectory and sunlight availability</b> for any location.
            </p>
            <p style="color:#ffffff; line-height:1.6;">
                The sun’s movement shifts significantly based on the seasons. Understanding these patterns is essential 
                for practical decisions—from <b>solar panel installation</b> and <b>garden landscaping</b> to ensuring a 
                potential <b>new home</b> receives enough natural light year-round.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # User Guide Section
    with st.expander("📖 HOW TO USE THE PORTAL", expanded=True):
        st.markdown("""
            1. **Select Your Location**: 
               Go to the **Location Setup** tab. Search for a city or double-click anywhere on the map to lock in coordinates.
            2. **Visualize the Movement**: 
               Switch to **Live Visualization**. Toggle the **Start Animation** button to see the sun sweep across the sky.
            3. **Understand the Map**:
               * <span style="color:#e74c3c; font-weight:bold;">● Red Line</span>: Direction of **Sunrise**.
               * <span style="color:#3498db; font-weight:bold;">● Blue Line</span>: Direction of **Sunset**.
               * <span style="color:#808080; font-weight:bold;">● Grey Line</span>: **Shadow Line** (where shadows will fall).
               * <span style="color:#f39c12; font-weight:bold;">● Orange Arc</span>: The actual **Sun Path** for your selected date.
        """, unsafe_allow_html=True)

    # Celestial Milestones Section
    st.markdown('<h4 class="theory-header" style="margin-top:20px;">📅 Celestial Milestones</h4>', unsafe_allow_html=True)
    
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.markdown("""
            <div class="milestone-card">
                <b style="color:#F7DF88;">Spring Equinox (Mar 20)</b><br>
                Day and night are approximately equal in length.
            </div>
            <div class="milestone-card" style="border-left-color: #3498db;">
                <b style="color:#72aee6;">Autumnal Equinox (Sep 22)</b><br>
                Marks the beginning of fall; equal day and night.
            </div>
        """, unsafe_allow_html=True)
    with col_eq2:
        st.markdown("""
            <div class="milestone-card">
                <b style="color:#F7DF88;">Summer Solstice (Jun 21)</b><br>
                The longest day of the year and the sun's highest path.
            </div>
            <div class="milestone-card" style="border-left-color: #3498db;">
                <b style="color:#72aee6;">Winter Solstice (Dec 21)</b><br>
                The shortest day of the year and the sun's lowest path.
            </div>
        """, unsafe_allow_html=True)

