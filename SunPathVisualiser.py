import streamlit as st 
import math
import requests
from datetime import datetime, date, timedelta
import pytz 
from timezonefinder import TimezoneFinder
from astral import LocationInfo 
from astral.sun import sunrise, sunset, noon, azimuth, elevation 
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components 
from streamlit_js_eval import get_geolocation

#----------------------------------------------------------------
# 1. UI STYLING
#----------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Solar Path Visualizer", page_icon="☀️")

st.markdown("""
    <style>
    .stApp { background: #0b0f19; }
    .main-title {
        color: #ffffff;
        font-weight: 800;
        text-align: center;
        letter-spacing: 3px;
        padding: 20px 0;
    }
    .obs-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 15px;
        height: 100%;
    }
    .sun-card {
        background: rgba(23, 33, 54, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        color: #72aee6;
        font-weight: 500;
    }
    .theory-section {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ccc;
    }
    .theory-header { color: #F7DF88; font-weight: 700; margin-bottom: 15px; }
    .milestone-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #f39c12;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 0 10px 10px 0;
    }
    [data-testid="stMetricValue"] { color: #f39c12 !important; font-weight: bold; }
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 15px;
    }
    .stTabs [aria-selected="true"] { color: #e74c3c !important; border-bottom-color: #e74c3c !important; }
    </style>
    """, unsafe_allow_html=True)

#----------------------------------------------------------------
# 2. CORE LOGIC & UTILITIES
#----------------------------------------------------------------
if 'coords' not in st.session_state:
    st.session_state.coords = [0.0, 0.0] 
    st.session_state.gps_requested = False

if not st.session_state.gps_requested:
    loc = get_geolocation()
    if loc:
        st.session_state.coords = [loc['coords']['latitude'], loc['coords']['longitude']]
        st.session_state.gps_requested = True
        st.rerun()

def search_city(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'SolarPathVisualizer_v1'}
        resp = requests.get(url, headers=headers).json()
        if resp:
            return [float(resp[0]['lat']), float(resp[0]['lon'])]
    except:
        return None
    return None

lat, lon = st.session_state.coords

@st.cache_data(ttl=600)
def get_environmental_data(lat, lon):
    api_key = "d4b056a2-a4bc-48d0-9a38-3f5a2c675ea7"
    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
    env = {"aqi": "N/A", "temp": "N/A", "hum": "N/A", "wind": "N/A", "color": "#444", "label": "Unknown"}
    try:
        r = requests.get(url, timeout=5).json()
        if r.get("status") == "success":
            data = r["data"]["current"]
            env.update({"aqi": data["pollution"]["aqius"], "temp": data["weather"]["tp"], "hum": data["weather"]["hu"], "wind": data["weather"]["ws"]})
            aqi = env["aqi"]
            if aqi <= 50: env["label"], env["color"] = "Good", "#00e400"
            elif aqi <= 100: env["label"], env["color"] = "Moderate", "#ffff00"
            elif aqi <= 150: env["label"], env["color"] = "Unhealthy(S)", "#ff7e00"
            else: env["label"], env["color"] = "Unhealthy", "#ff0000"
    except: pass
    return env

loc_key = f"{lat}_{lon}"
if "last_loc_key" not in st.session_state or st.session_state.last_loc_key != loc_key:
    st.session_state.env_data = get_environmental_data(lat, lon)
    st.session_state.last_loc_key = loc_key
env_data = st.session_state.env_data

tf = TimezoneFinder()
tz_name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
local_tz = pytz.timezone(tz_name)
city_info = LocationInfo(timezone=tz_name, latitude=lat, longitude=lon)

def get_solar_pos(t, r, clat, clon):
    az_val = azimuth(city_info.observer, t)
    el_val = elevation(city_info.observer, t)
    # Project sun position onto a 2D map plane based on elevation/azimuth
    sc = math.cos(math.radians(max(0, el_val)))
    slat = clat + (r * sc / 111111) * math.cos(math.radians(az_val))
    slon = clon + (r * sc / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az_val))
    # Shadow logic (opposite to sun)
    shlat = clat + (r * 0.7 / 111111) * math.cos(math.radians(az_val + 180))
    shlon = clon + (r * 0.7 / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az_val + 180))
    return slat, slon, shlat, shlon, az_val, el_val

def get_edge(az_input, radius):
    rad = math.radians(az_input)
    return [lat + (radius/111111)*math.cos(rad), lon + (radius/(111111*math.cos(math.radians(lat))))*math.sin(rad)]

#---------------------------------------------------------------
# 3. SIDEBAR
#---------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    with st.form("city_search"):
        search_query = st.text_input("🔍 Search City", placeholder="e.g. Paris, France")
        search_btn = st.form_submit_button("Search")
        if search_btn and search_query:
            coords = search_city(search_query)
            if coords:
                st.session_state.coords = coords
                st.rerun()
            else:
                st.error("City not found!")

    if st.button("📍 Reset to My GPS"):
        st.session_state.gps_requested = False
        st.rerun()
        
    st.markdown("---")
    st.subheader("📅 Date Selection")
    celestial_dates = {
        "Manual Selection": None,
        "Spring Equinox (Mar 20)": date(2026, 3, 20),
        "Summer Solstice (Jun 21)": date(2026, 6, 21),
        "Autumnal Equinox (Sep 22)": date(2026, 9, 22),
        "Winter Solstice (Dec 21)": date(2026, 12, 21)
    }
    date_preset = st.selectbox("Key Celestial Dates", list(celestial_dates.keys()))
    target_date = celestial_dates[date_preset] if date_preset != "Manual Selection" else st.date_input("Select Date", date.today())
    
    radius_meters = 250
    st.markdown("---")
    st.subheader("🌐 Environment")
    enable_aqi = st.toggle("Show Live AQI & Weather", value=False)
    
    st.markdown("---")
    shour = st.slider("Hour", 0, 23, datetime.now(local_tz).hour)
    smin = st.slider("Minute", 0, 59, 0)
    sim_time = local_tz.localize(datetime.combine(target_date, datetime.min.time())) + timedelta(hours=shour, minutes=smin)

    try:
        rise_t = sunrise(city_info.observer, date=target_date, tzinfo=local_tz)
        set_t = sunset(city_info.observer, date=target_date, tzinfo=local_tz)
        noon_t = noon(city_info.observer, date=target_date, tzinfo=local_tz)
    except:
        # Handle polar regions/errors
        rise_t = sim_time.replace(hour=6, minute=0)
        set_t = sim_time.replace(hour=18, minute=0)
        noon_t = sim_time.replace(hour=12, minute=0)

#---------------------------------------------------------------
# 4. SHARED RENDERERS
#---------------------------------------------------------------
def render_dashboard_footer(key_suffix):
    st.markdown("---")
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = get_solar_pos(sim_time, radius_meters, lat, lon)

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Selected Time", sim_time.strftime('%H:%M'))
    m_col2.metric("Azimuth", f"{m_az:.1f}°")
    m_col3.metric("Elevation", f"{m_el:.1f}°")
    m_col4.metric("Solar Noon", noon_t.strftime('%H:%M'))

    if enable_aqi:
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        w_col1.metric("🌡️ Temp", f"{env_data['temp']}°C")
        w_col2.metric("💧 Humidity", f"{env_data['hum']}%")
        w_col3.metric("🌬️ Wind", f"{env_data['wind']} m/s")
        w_col4.metric("💨 AQI", env_data["aqi"], delta=env_data["label"], delta_color="inverse")

    # Chart Data Generation
    path_pts = []
    temp_curr = rise_t
    while temp_curr <= set_t:
        _, _, _, _, _, el = get_solar_pos(temp_curr, radius_meters, lat, lon)
        path_pts.append({"time": temp_curr.strftime("%H:%M"), "el": el})
        temp_curr += timedelta(minutes=15)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[p['time'] for p in path_pts], 
        y=[p['el'] for p in path_pts], 
        mode='lines', 
        line=dict(color='#f39c12', width=3),
        fill='tozeroy',
        fillcolor='rgba(243, 156, 18, 0.1)'
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Elevation (°)"))
    
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")
    

#---------------------------------------------------------------
# 5. MAIN UI LAYOUT
#---------------------------------------------------------------
st.markdown('<h1 class="main-title">☀️SOLAR PATH VISUALIZER☀️</h1>', unsafe_allow_html=True)

top_col1, top_col2 = st.columns([2.5, 1])
with top_col1:
    st.markdown(f"""
        <div class="obs-card">
            <h4 style="color:#F7DF88; margin-top:0;">🗺️Where are you?</h4>
            <p style="color:#ccc; font-size:0.95rem; line-height:1.6;">
                Tracking solar trajectory at <b>{lat:.4f}, {lon:.4f}</b>.<br>
                The <span style="color:#e74c3c; font-weight:bold;">red line</span> is sunrise, 
                <span style="color:#3498db; font-weight:bold;">blue</span> is sunset, 
                <span style="color:#808080; font-weight:bold;">grey</span> is the shadow line.
            </p>
        </div>
        """, unsafe_allow_html=True)
with top_col2:
    st.markdown(f'<div class="sun-card">🌅 Sunrise: {rise_t.strftime("%H:%M")}<br><br>🌇 Sunset: {set_t.strftime("%H:%M")}<br><br>💨AQI: {env_data["aqi"] if enable_aqi else "Disabled"}</div>', unsafe_allow_html=True)

tab_info, tab1, tab2 = st.tabs(["📖 Guide & Theory", "📍 Location Setup", "🚀 Live Visualization"])

with tab_info:
    st.markdown("""
        <div class="theory-section">
            <h2 class="theory-header">☀️ About Solar Path Visualizer</h2>
            <p style="color:#ccc; line-height:1.6;">
                Have you ever wondered about the exact movement of the sun or how much sunlight a specific spot on Earth receives? 
                This tool is designed to showcase the <b>solar trajectory and sunlight availability</b> for any location.
            </p>
            <p style="color:#ccc; line-height:1.6;">
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

with tab1:
    m = folium.Map(location=st.session_state.coords, zoom_start=17, tiles=None)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite').add_to(m)
    folium.TileLayer('openstreetmap', name='Street').add_to(m)
    folium.LayerControl().add_to(m)
    folium.Marker(st.session_state.coords, icon=folium.Icon(color='orange', icon='sun', prefix='fa')).add_to(m)
    
    map_data = st_folium(m, height=450, use_container_width=True, key="selection_map")
    if map_data and map_data.get("last_clicked"):
        st.session_state.coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        st.rerun()
    render_dashboard_footer("location")

with tab2:
    animate_trigger = st.toggle("🚀 Start Animation", key="anim_toggle")
    
    # Generate path for the day
    path_data = []
    curr = rise_t
    while curr <= set_t:
        slat, slon, shlat, shlon, az, el = get_solar_pos(curr, radius_meters, lat, lon)
        path_data.append({"lat": slat, "lon": slon, "shlat": shlat, "shlon": shlon, "time": curr.strftime("%H:%M"), "el": el})
        curr += timedelta(minutes=10)

    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = get_solar_pos(sim_time, radius_meters, lat, lon)

    if m_el <= 0:
        st.warning(f"🌙 The sun is currently below the horizon ({m_el:.1f}°).")

    map_html = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map2" style="height: 550px; width: 100%; border-radius: 12px; border: 1px solid #444;"></div>
        <script>
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            
            var map2 = L.map('map2', {{ center: [{lat}, {lon}], zoom: 17, layers: [satellite] }});
            L.control.layers({{"Satellite": satellite, "Street": street}}, null, {{collapsed: false}}).addTo(map2);

            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'white', weight: 1, fillOpacity: 0.1}}).addTo(map2);
            L.marker([{lat}, {lon}]).addTo(map2);

            var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5, opacity: 0.8}}).addTo(map2);
            
            // Fixed line endpoint logic
            L.polyline([[{lat}, {lon}], {get_edge(azimuth(city_info.observer, rise_t), radius_meters)}], {{color: '#e74c3c', weight: 3}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {get_edge(azimuth(city_info.observer, set_t), radius_meters)}], {{color: '#3498db', weight: 3}}).addTo(map2);

            var sunIcon = L.divIcon({{
                html: '<div class="sun-container"><div id="sun-time" class="sun-label"></div><div class="sun-emoji">☀️</div></div>', 
                iconSize: [100, 100], iconAnchor: [50, 50], className: 'custom-sun-icon'
            }});
            
            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadowLine = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);

            function updateFrame(pos) {{
                if (pos && pos.el > -0.5) {{
                    sunMarker.setOpacity(1); 
                    shadowLine.setStyle({{opacity: 0.5}});
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadowLine.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                    document.getElementById('sun-time').innerHTML = pos.time;
                }} else {{
                    sunMarker.setOpacity(0); shadowLine.setStyle({{opacity: 0}});
                }}
            }}

            if ({str(animate_trigger).lower()}) {{
                var i = 0;
                function doAnimate() {{
                    updateFrame(pathData[i]);
                    i = (i + 1) % pathData.length;
                    setTimeout(doAnimate, 100);
                }}
                doAnimate();
            }} else {{
                updateFrame({{lat: {m_slat}, lon: {m_slon}, shlat: {m_shlat}, shlon: {m_shlon}, time: "{sim_time.strftime('%H:%M')}", el: {m_el}}});
            }}
        </script>
        <style>
            .custom-sun-icon {{ background: none !important; border: none !important; }}
            .sun-container {{ display: flex; position: relative; align-items: center; justify-content: center; width: 100px; height: 100px; }}
            .sun-label {{ background: rgba(0,0,0,0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10pt; position: absolute; top: 0px; border: 1px solid #f39c12; font-family: sans-serif; white-space: nowrap; }}
            .sun-emoji {{ font-size: 32pt; }}
        </style>
    """
    components.html(map_html, height=570)
    render_dashboard_footer("visualisation")

