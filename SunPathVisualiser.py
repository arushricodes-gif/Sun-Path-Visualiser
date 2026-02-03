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
# --- NEW IMPORT FOR GPS ---
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
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
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
# 2. GPS DETECTION & LOGIC
#----------------------------------------------------------------
# Initialize coordinates with a default, but try to get GPS first
if 'coords' not in st.session_state:
    st.session_state.coords = [0, 0] # Default fallback
    st.session_state.gps_requested = False

# Request GPS location once per session
if not st.session_state.gps_requested:
    loc = get_geolocation()
    if loc:
        st.session_state.coords = [loc['coords']['latitude'], loc['coords']['longitude']]
        st.session_state.gps_requested = True
        st.rerun()

lat, lon = st.session_state.coords

@st.cache_data(ttl=600)
def get_environmental_data(lat, lon):
    api_key = "d4b056a2-a4bc-48d0-9a38-3f5a2c675ea7"
    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
    env = {"aqi": "N/A", "temp": "N/A", "hum": "N/A", "wind": "N/A", "color": "#444", "label": "Unknown"}
    try:
        r = requests.get(url, timeout=10).json()
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
city = LocationInfo(timezone=tz_name, latitude=lat, longitude=lon)

#---------------------------------------------------------------
# 3. SIDEBAR & TIME CONTROL
#---------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("📍 Reset to My GPS"):
        st.session_state.gps_requested = False
        st.rerun()
        
    target_date = st.date_input("Select Date", date.today())
    if target_date != date.today():
        st.warning("Weather/AQI data reflects LIVE conditions.")
    radius_meters = st.slider("Visual Radius (m)", 50, 500, 150)
    
    try:
        rise_t = sunrise(city.observer, date=target_date, tzinfo=local_tz)
        set_t = sunset(city.observer, date=target_date, tzinfo=local_tz)
        noon_t = noon(city.observer, date=target_date, tzinfo=local_tz)
    except:
        rise_t = local_tz.localize(datetime.combine(target_date, datetime.min.time())) + timedelta(hours=7)
        set_t = local_tz.localize(datetime.combine(target_date, datetime.min.time())) + timedelta(hours=18)
    
    st.markdown("---")
    shour = st.slider("Hour", 0, 23, datetime.now(local_tz).hour)
    smin = st.slider("Minute", 0, 59, 0)
    sim_time = local_tz.localize(datetime.combine(target_date, datetime.min.time())) + timedelta(hours=shour, minutes=smin)

#---------------------------------------------------------------
# 4. DASHBOARD HEADER
#---------------------------------------------------------------
st.markdown('<h1 class="main-title">☀️SOLAR PATH VISUALIZER☀️</h1>', unsafe_allow_html=True)

top_col1, top_col2 = st.columns([2.5, 1])
with top_col1:
    st.markdown(f"""
        <div class="obs-card">
            <h4 style="color:#F7DF88; margin-top:0;">📋 How it works</h4>
            <p style="color:#ccc; font-size:0.95rem; line-height:1.6;">
                Tracking solar trajectory at <b>{lat:.4f}, {lon:.4f}</b>: Select your particular location on <b>Tab 1</b>. Switch to the <b>2nd Tab</b> to see the solar path animation.<br>
                The <span style="color:#e74c3c; font-weight:bold;">red line</span> represents sunrise, 
                <span style="color:#3498db; font-weight:bold;">blue</span> shows sunset, 
                <span style="color:#808080; font-weight:bold;">grey</span> shows the shadow line and the 
                <span style="color:#f39c12; font-weight:bold;">orange arc</span> shows the sun path on the paritcular dayandtime selected.
            </p>
        </div>
        """, unsafe_allow_html=True)
with top_col2:
    st.markdown(f"""
        <div class="sun-card">
            🌅 Sunrise: {rise_t.strftime('%H:%M')}<br><br>
            🌇 Sunset: {set_t.strftime('%H:%M')}<br><br>
            💨AQI: {env_data['aqi']}
        </div>
        """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📍 Location Setup", "🚀 Live Visualization"])

with tab1:
    m = folium.Map(location=st.session_state.coords, zoom_start=17, tiles=None)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite View', overlay=False).add_to(m)
    folium.TileLayer('openstreetmap', name='Street View', overlay=False).add_to(m)
    folium.LayerControl().add_to(m)
    folium.Marker(st.session_state.coords, icon=folium.Icon(color='orange', icon='sun', prefix='fa')).add_to(m)
    
    map_data = st_folium(m, height=450, use_container_width=True, key="selection_map")
    if map_data and map_data.get("last_clicked"):
        st.session_state.coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        st.rerun()

with tab2:
    def get_solar_pos(t, r, clat, clon):
        az = azimuth(city.observer, t); el = elevation(city.observer, t)
        sc = math.cos(math.radians(max(0, el)))
        slat = clat + (r * sc / 111111) * math.cos(math.radians(az))
        slon = clon + (r * sc / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az))
        shlat = clat + (r * 0.7 / 111111) * math.cos(math.radians(az + 180))
        shlon = clon + (r * 0.7 / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az + 180))
        return slat, slon, shlat, shlon, az, el

    def get_edge(az):
        rad = math.radians(az)
        return [lat + (radius_meters/111111)*math.cos(rad), lon + (radius_meters/(111111*math.cos(math.radians(lat))))*math.sin(rad)]

    animate_trigger = st.toggle("🚀 Start Animation", key="anim_toggle")
    
    path_data = []
    curr = rise_t
    while curr <= set_t:
        slat, slon, shlat, shlon, az, el = get_solar_pos(curr, radius_meters, lat, lon)
        path_data.append({"lat": slat, "lon": slon, "shlat": shlat, "shlon": shlon, "time": curr.strftime("%H:%M"), "el": el})
        curr += timedelta(minutes=5)

    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = get_solar_pos(sim_time, radius_meters, lat, lon)

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

            var data = {path_data};
            L.polyline(data.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5, opacity: 0.8}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {get_edge(azimuth(city.observer, rise_t))}], {{color: '#e74c3c', weight: 3}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {get_edge(azimuth(city.observer, set_t))}], {{color: '#3498db', weight: 3}}).addTo(map2);

            var sunIcon = L.divIcon({{
                html: '<div class="sun-container"><div id="sun-time" class="sun-label"></div><div class="sun-emoji">☀️</div></div>', 
                iconSize: [100, 100], iconAnchor: [50, 50], className: 'custom-sun-icon'
            }});
            
            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadowLine = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);

            function updateFrame(pos) {{
                if (pos && pos.el > 0) {{
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
                    updateFrame(data[i]);
                    i = (i + 1) % data.length;
                    setTimeout(doAnimate, 80);
                }}
                doAnimate();
            }} else {{
                updateFrame({{lat: {m_slat}, lon: {m_slon}, shlat: {m_shlat}, shlon: {m_shlon}, time: "{sim_time.strftime('%H:%M')}", el: {m_el}}});
            }}
        </script>
        <style>
            .custom-sun-icon {{ background: none !important; border: none !important; }}
            .sun-container {{ display: flex; position: relative; align-items: center; justify-content: center; width: 100px; height: 100px; }}
            .sun-label {{ background: rgba(0,0,0,0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10pt; position: absolute; top: 0px; border: 1px solid #f39c12; font-family: sans-serif; }}
            .sun-emoji {{ font-size: 32pt; }}
        </style>
    """
    components.html(map_html, height=570)

#---------------------------------------------------------------
# 5. METRICS, AQI BAR & CHART
#---------------------------------------------------------------
st.markdown("---")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Selected Time", sim_time.strftime('%H:%M'))
m_col2.metric("Azimuth", f"{m_az:.1f}°")
m_col3.metric("Elevation", f"{m_el:.1f}°")
m_col4.metric("Solar Noon", noon_t.strftime('%H:%M'))

w_col1, w_col2, w_col3, w_col4 = st.columns(4)
w_col1.metric("🌡️ Temp", f"{env_data['temp']}°C")
w_col2.metric("💧 Humidity", f"{env_data['hum']}%")
w_col3.metric("🌬️ Wind", f"{env_data['wind']} m/s")
w_col4.metric("💨 AQI", env_data["aqi"], delta=env_data["label"], delta_color="inverse")

aqi_val = env_data['aqi'] if isinstance(env_data['aqi'], int) else 0
bar_percentage = min((aqi_val / 300) * 100, 100) 

st.markdown(f"""
    <div style="margin-top: 20px; margin-bottom: 5px; color: #ccc; font-size: 0.85rem; font-weight: bold;">
        LIVE AIR QUALITY INDEX (AQI) VISUALIZER
    </div>
    <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 10px; height: 18px; border: 1px solid rgba(255,255,255,0.05); overflow: hidden;">
        <div style="width: {bar_percentage}%; 
                    background: {env_data['color']}; 
                    height: 100%; 
                    border-radius: 10px; 
                    box-shadow: 0 0 15px {env_data['color']}; 
                    transition: width 1s ease-in-out;">
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.7rem; color: #888;">
        <span>GOOD (0-50)</span>
        <span>MODERATE (51-100)</span>
        <span>UNHEALTHY (101-200)</span>
        <span>HAZARDOUS (300+)</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
curve_times = [rise_t + timedelta(minutes=10*i) for i in range(len(path_data))]
curve_els = [d['el'] for d in path_data]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[t.strftime("%H:%M") for t in curve_times], 
    y=curve_els, 
    mode='lines', 
    line=dict(color='#f39c12', width=3),
    fill='tozeroy',
    fillcolor='rgba(243, 156, 18, 0.1)'
))

fig.add_hrect(y0=0, y1=6, fillcolor="gold", opacity=0.1, line_width=0, annotation_text="Golden Hour")
fig.add_hrect(y0=-6, y1=0, fillcolor="royalblue", opacity=0.1, line_width=0, annotation_text="Twilight")

fig.update_layout(
    height=250, 
    margin=dict(l=10, r=10, t=30, b=10), 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)', 
    font_color="white",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Elevation (°)")
)
st.plotly_chart(fig, use_container_width=True)
