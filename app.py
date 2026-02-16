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
    # Logic fix to prevent KeyError
    if loc and 'coords' in loc:
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
# --- SIDEBAR SEARCH FIX ---
with st.sidebar:
    st.header("⚙️ Settings")
    with st.form("city_search"):
        search_query = st.text_input("🔍 Search for place", placeholder="e.g. Paris, France")
        # The Submit button is required for st.form to work
        submitted = st.form_submit_button("Search Location")
        
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

# --- FOOTER RENDERER ---
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
    fig.update_layout(
        height=250, 
        margin=dict(l=10, r=10, t=30, b=10), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font_color="black", 
        xaxis=dict(showgrid=False, color="black"), 
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(0,0,0,0.1)', 
            title="Elevation (°)",
            color="black"
        )
    )
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")

st.markdown('<h3 class="main-title">☀️ SOLAR PATH VISUALIZER ☀️</h3>', unsafe_allow_html=True)
top_col1, top_col2 = st.columns([2.5, 1])

tab1, tab2, tab_info, tab_summary = st.tabs(["Step 1: 📍 Location Setup", "Step 2: 🚀 Live Visualization", "📖 How it works?", "Year Round Summary"])

with tab1:
    m = folium.Map(location=st.session_state.coords, zoom_start=17)
    st.markdown("Select your location on the map and follow on to step 2.")
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite').add_to(m)
    folium.TileLayer('openstreetmap', name='Street').add_to(m)
    folium.LayerControl().add_to(m)
    folium.Marker(st.session_state.coords, icon=folium.Icon(color='orange', icon='sun', prefix='fa')).add_to(m)
    map_data = st_folium(m, height=700, use_container_width=True, key="selection_map")
    if map_data and map_data.get("last_clicked"):
        st.session_state.coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        st.rerun()
    render_dashboard_footer("location")

with tab2:
    animate_trigger = st.toggle("Play Path", value=True, key="anim_toggle")
    path_data = []
    curr = rise_t
    while curr <= set_t:
        slat, slon, shlat, shlon, az, el = solarlogic.get_solar_pos(city_info, curr, radius_meters, lat, lon)
        path_data.append({"lat": slat, "lon": slon, "shlat": shlat, "shlon": shlon, "time": curr.strftime("%H:%M"), "el": el})
        curr += timedelta(minutes=10)
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(city_info, sim_time, radius_meters, lat, lon)
    if m_el <= 0: st.warning(f"🌙 The sun is currently below the horizon ({m_el:.1f}°).")
    
    rise_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, rise_t), radius_meters)
    set_edge = solarlogic.get_edge(lat, lon, azimuth(city_info.observer, set_t), radius_meters)
    

    visuals.render_map_component(
        lat, lon, radius_meters, path_data, animate_trigger, sim_time, 
        m_slat, m_slon, m_shlat, m_shlon, m_el, rise_edge, set_edge,
        rise_t.strftime("%H:%M"), 
        set_t.strftime("%H:%M"), 
        env_data["aqi"] if enable_aqi else "Off"
    )
    render_dashboard_footer("visualisation")

with tab_info:
    # Restored Your Original Info Content
    st.markdown("""
        <div class="theory-section">
            <h1 class="theory-header">☀️ About Solar Path Visualizer</h1>
            <p>Have you ever wondered about the exact movement of the sun or how much sunlight a specific spot on Earth receives? This tool is designed to showcase the <b>solar trajectory and sunlight availability</b> for any location.</p>
            <p>The sun’s movement shifts significantly based on the seasons. Understanding these patterns is essential for practical decisions—from <b>solar panel installation</b> and <b>garden landscaping</b> to ensuring a potential <b>new home</b> receives enough natural light year-round.</p>
        </div>

        <h2 class="theory-header">🔍 How to Use</h2>
        <div class="milestone-card"><b>1. Select Your Location:</b> Go to Location Setup tab. Search or double-click the map.</div>
        <div class="milestone-card"><b>2. Visualize:</b> Switch to Live Visualization. Toggle 'Start Animation'.</div>
        
        <h2 class="theory-header">🗺️ Line Index (Map Legend)</h2>
        <div class="legend-container">
            <div class="legend-item" style="color:#e74c3c;">🔴 Sunrise Line</div>
            <div class="legend-item" style="color:#3498db;">🔵 Sunset Line</div>
            <div class="legend-item" style="color:#808080;">⚪ Shadow Line</div>
            <div class="legend-item" style="color:#f39c12;">🟠 Solar Path</div>
        </div>

        <h2 class="theory-header" style="margin-top:30px;">📅 Celestial Milestones</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div class="milestone-card"><b>Spring Equinox (Mar 20)</b><br>Day and night equal length.</div>
            <div class="milestone-card"><b>Summer Solstice (Jun 21)</b><br>Longest day, highest path.</div>
            <div class="milestone-card"><b>Autumnal Equinox (Sep 22)</b><br>Equal day and night.</div>
            <div class="milestone-card"><b>Winter Solstice (Dec 21)</b><br>Shortest day, lowest path.</div>
        </div>
    """, unsafe_allow_html=True)


with tab_summary:
    st.markdown('<div class="theory-section"><h2 class="theory-header">📅 Seasonal Comparison</h2></div>', unsafe_allow_html=True)
    
    # We use a list of dictionaries so we can keep the ID separate from the Display Name
    milestones = [
        {"id": "Summer", "label": "Summer (June 21)", "date": date(2026, 6, 21)},
        {"id": "Autumn", "label": "Autumn (Oct 31)", "date": date(2026, 10, 31)},
        {"id": "Spring", "label": "Spring (March 20)", "date": date(2026, 3, 20)},
        {"id": "Winter", "label": "Winter (Dec 21)", "date": date(2026, 12, 21)}
    ]
    
    seasonal_data = {}
    for m in milestones:
        m_date = m["date"]
        m_r = sunrise(city_info.observer, date=m_date, tzinfo=local_tz)
        m_s = sunset(city_info.observer, date=m_date, tzinfo=local_tz)
        pts = []
        c = m_r
        while c <= m_s:
            lat_p, lon_p, _, _, _, _ = solarlogic.get_solar_pos(city_info, c, radius_meters, lat, lon)
            pts.append([lat_p, lon_p])
            c += timedelta(minutes=20)
        # Store both the points and the label
        seasonal_data[m["id"]] = {"coords": pts, "label": m["label"]}

    visuals.render_seasonal_map(lat, lon, radius_meters, seasonal_data)
    
    st.markdown("""
    <div style="display: flex; justify-content: space-around; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px;">
        <div style="color:#FF0000;">● Summer</div>
        <div style="color:#FF8C00;">● Autumn</div>
        <div style="color:#FFD700;">● Spring</div>
        <div style="color:#FFFF00;">● Winter</div>
    </div>""", unsafe_allow_html=True)

