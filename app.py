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
import json
import os

import visuals
import solarlogic

st.set_page_config(layout="wide", page_title="Solar Path Visualizer", page_icon="☀️")
visuals.apply_styles()

if 'coords' not in st.session_state:
    st.session_state.coords = [0.0, 0.0] 
    st.session_state.gps_requested = False

if not st.session_state.gps_requested:
    loc = get_geolocation()
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
with st.sidebar:
    st.header("⚙️ Settings")
    with st.form("city_search"):
        search_query = st.text_input("🔍 Search for place", placeholder="e.g. Paris, France")
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

    if date_preset == "Manual Selection":
        target_date = st.date_input("Select Date", date.today())
    else:
        target_date = celestial_dates[date_preset]
        
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

st.markdown('<h1 class="main-title">☀️ SunScout: The Solar Path Visualizer ☀️</h1>', unsafe_allow_html=True)
top_col1, top_col2 = st.columns([2.5, 1])

tab_info, tab1, tab2, tab_summary, tab_comments = st.tabs(["📖 What's this?", "Step 1: 📍 Location Setup", "Step 2: 🚀 Live Visualization",  "🔄 Year Round Summary", "👤 User Comments"])

with tab_info:
    st.markdown("""
<div style="color: white; font-family: 'Inter', sans-serif;">
<h2 style="color: white;">🤩 Let the Sun guide your next big decision. </h2>
<p>Ever wondered how much sunlight your <b>bedroom, balcony, terrace garden,</b> or <b>solar panels</b> will get throughout the year? Now you don't have to guess.</p>

<hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">

<h3 style="color: white;">🌍 What Solar Path Visualizer Does</h3>
<p>A simple, educational, purpose-built tool that <b>instantly shows how sunlight moves across any location on Earth</b>, across <b>all seasons</b>, in a clean, intuitive interface. Use it to make confident, informed decisions whether you are:</p>
<ul style="list-style-type: none; padding-left: 20px; line-height: 2;">
    <li>🏠 <b>Buying a new home</b></li>
    <li>🌿 <b>Planning a balcony or terrace garden</b></li>
    <li>☀️ <b>Installing a solar geyser or solar panels</b></li>
    <li>🏙️ <b>Checking how sunlight enters a specific window or corner</b></li>
</ul>

<hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">

<h3 style="color: white;">☀️ Why This Matters</h3>
<p>The sun's position changes every day. <b>Solstices, equinoxes, and shifting sunrise and sunset angles</b> all affect how light reaches your spaces. A room that's bright in winter may be dim in summer. A terrace perfect for plants in spring may be shaded in autumn. This tool shows you <b>exact sun behavior</b>, so you can plan smarter.</p>

<hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">

<h3 style="color: white;">🔍 How to Use Solar Path Visualizer</h3>

<p>📍 <b>Select Your Location</b></p>
<p style="padding-left: 20px;">Go to the <b>Location Setup</b> tab. Search for a city or <b>double-click anywhere on the map</b> to lock in coordinates. Also select the date or season you are looking for.</p>

<p>⏯️ <b>Visualize the Movement</b></p>
<p style="padding-left: 20px;">Switch to <b>Live Visualization</b>. Toggle the <b>Play Path</b> button to watch the sun sweep across the sky for your chosen date and time.</p>

<p>🗺️ <b>Understand the Map</b></p>
<ul style="list-style-type: none; padding-left: 20px; line-height: 2;">
    <li><span style="color: #e74c3c; font-size: 20px;">🔴</span> <b>Red Line:</b> Direction of <b>Sunrise</b></li>
    <li><span style="color: #3498db; font-size: 20px;">🔵</span> <b>Blue Line:</b> Direction of <b>Sunset</b></li>
    <li><span style="color: #808080; font-size: 20px;">⚪</span> <b>Grey Line: Shadow Line</b> showing where shadows will fall</li>
    <li><span style="color: #f39c12; font-size: 20px;">🟠</span> <b>Orange Arc:</b> The actual <b>Sun Path</b> for your selected date</li>
</ul>

<p>🔄 <b>Look at the Entire Year's Summary</b></p>
<p style="padding-left: 20px;">On switching to this tab, you can see the key paths the sun follows at the selected location during the main four seasons.</p>

<hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">

<h3 style="color: white;">🧭 Quick Use Cases</h3>
<ul style="list-style-type: none; padding-left: 10px; line-height: 1.8;">
    <li>🏠 <b>Home Buyers:</b> Compare sunlight for different apartments or orientations before you commit.</li>
    <li>🌱 <b>Gardeners:</b> Pick the best spots and plant types for balconies and terraces.</li>
    <li>🔌 <b>Solar planners:</b> Estimate panel exposure and optimize placement for maximum yield.</li>
    <li>📐 <b>Architects and renovators:</b> Design with daylighting and occupant comfort in mind.</li>
</ul>
</div>
""", unsafe_allow_html=True)

with tab1:
    display_lat = f"{st.session_state.coords[0]:.5f}"
    display_lon = f"{st.session_state.coords[1]:.5f}"
    display_date = target_date.strftime("%B %d, %Y") 
  
    map_key = f"map_select_{target_date}_{st.session_state.coords[0]}"
    
    m = folium.Map(location=st.session_state.coords, zoom_start=17, tiles=None)

    # Satellite Layer
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
        attr='Esri', 
        name='Satellite'
    ).add_to(m)
    
    # Street Layer
    folium.TileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
        attr='&copy; OpenStreetMap contributors', 
        name='Street'
    ).add_to(m)

    folium.LayerControl(position='topleft', collapsed=False).add_to(m)

    folium.Marker(st.session_state.coords, icon=folium.Icon(color='orange', icon='sun', prefix='fa')).add_to(m)

    info_html = f'''
        <div style="
            position: absolute; 
            top: 10px; right: 10px; 
            width: 180px;
            background: rgba(14, 17, 23, 0.9); 
            padding: 12px; 
            border-radius: 10px;
            border: 2px solid #F39C12; 
            color: white; 
            font-family: 'Inter', sans-serif; 
            font-size: 13px;
            z-index: 1000;
            pointer-events: none;
            ">
            <div style="color:#F39C12; font-weight:bold; font-size: 11px; letter-spacing: 1px;">📍 LOCATION</div>
            <div style="margin-bottom: 8px;">{display_lat}, {display_lon}</div>
            <div style="color:#F39C12; font-weight:bold; font-size: 11px; letter-spacing: 1px;">📅 SELECTED DATE</div>
            <div>{display_date}</div>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(info_html))

    st.markdown("Select your location and date/Season of interest [Default it picks your present location and present date]. Then switch to Step 2: Live Visualization to see the Sun's Path.")
    
    map_data = st_folium(
        m, 
        height=700, 
        use_container_width=True, 
        key=map_key 
    )

    if map_data and map_data.get("last_clicked"):
        new_coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        if new_coords != st.session_state.coords:
            st.session_state.coords = new_coords
            st.rerun()

    render_dashboard_footer("location")


with tab2:
    animate_trigger = st.toggle("Play Path", value=True, key="anim_toggle")  
    st.markdown("For selected date and time.")
    path_data = []
    curr = rise_t
    while curr <= set_t:
        slat, slon, shlat, shlon, az, el = solarlogic.get_solar_pos(city_info, curr, radius_meters, lat, lon)
        path_data.append({"lat": slat, "lon": slon, "shlat": shlat, "shlon": shlon, "time": curr.strftime("%H:%M"), "el": el})
        curr += timedelta(minutes=10)
    m_slat, m_slon, m_shlat, m_shlon, m_az, m_el = solarlogic.get_solar_pos(city_info, sim_time, radius_meters, lat, lon)
    if m_el <= 0: st.warning(f"🌅 The sun is currently below the horizon ({m_el:.1f}°).")
    
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


with tab_summary:
    st.markdown('<div class="theory-section"><h2 class="theory-header">Seasonal Comparison</h2></div>', unsafe_allow_html=True)
    
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
        seasonal_data[m["id"]] = {"coords": pts, "label": m["label"]}

    visuals.render_seasonal_map(lat, lon, radius_meters, seasonal_data)
    
    st.markdown("""
    <div style="display: flex; justify-content: space-around; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px;">
        <div style="color:#FF0000;">● Summer</div>
        <div style="color:#FF8C00;">● Autumn</div>
        <div style="color:#FFD700;">● Spring</div>
        <div style="color:#FFFF00;">● Winter</div>
    </div>""", unsafe_allow_html=True)


import json
import os
import requests
from datetime import datetime

# --- CONFIGURATION ---
COMMENTS_FILE = "user_comments.json"
# 1. Update this to your actual email to get alerts!
MY_EMAIL = "your-email@example.com" 

# 2. MATCHING YOUR SECRET NAME
if "MY_PASSWORD" in st.secrets:
    CORRECT_PASSWORD = st.secrets["MY_PASSWORD"]
else:
    # This is the fallback if secrets are not found
    CORRECT_PASSWORD = "admin" 

# --- HELPER FUNCTIONS ---
def load_comments():
    if os.path.exists(COMMENTS_FILE):
        try:
            with open(COMMENTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_comment(user_name, comment_text):
    comments = load_comments()
    new_comment = {
        "name": user_name,
        "text": comment_text,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    comments.append(new_comment)
    with open(COMMENTS_FILE, "w") as f:
        json.dump(comments, f)
    return new_comment

# --- THE COMMENTS TAB ---
with tab_comments:
    st.markdown("### 💬 User Feedback & Comments")
    
    # 1. SECURE ADMIN TOOLS (Access via URL ?admin=true)
    if st.query_params.get("admin") == "true":
        with st.expander("🔐 Admin JSON Management", expanded=True):
            password_guess = st.text_input("Enter Admin Password", type="password")
            
            if password_guess == CORRECT_PASSWORD:
                st.success("Access Granted")
                col_a, col_b = st.columns(2)
                
                if os.path.exists(COMMENTS_FILE):
                    with open(COMMENTS_FILE, "r") as f:
                        raw_data = f.read()
                    
                    col_a.download_button(
                        label="📥 Download JSON Backup",
                        data=raw_data,
                        file_name="user_comments.json",
                        mime="application/json"
                    )
                    
                    if col_b.button("🗑️ Clear All Comments"):
                        with open(COMMENTS_FILE, "w") as f:
                            json.dump([], f)
                        st.success("JSON cleared!")
                        st.rerun()
                    
                    st.markdown("**Current Data:**")
                    st.json(load_comments())
            elif password_guess != "":
                st.error("Incorrect Password")

    # 2. COMMENT FORM
    with st.form("comment_form", clear_on_submit=True):
        st.write("Post a comment or suggestion below:")
        u_name = st.text_input("Name", placeholder="Your Name")
        u_text = st.text_area("Message", placeholder="What do you think of SunScout?")
        submitted = st.form_submit_button("Post Comment")
        
        if submitted:
            if u_name and u_text:
                # Save locally to JSON
                new_data = save_comment(u_name, u_text)
                
                # Email Notification
                try:
                    requests.post(f"https://formsubmit.co/ajax/{MY_EMAIL}", 
                                  data={"Name": u_name, "Comment": u_text, "Time": new_data['time']})
                except:
                    pass 
                
                st.toast(f"Thanks {u_name}! Your comment is live.")
                st.rerun()
            else:
                st.warning("Please fill in both fields.")

    st.markdown("---")
    
    # 3. DISPLAY COMMENTS (Public)
    display_data = load_comments()
    if not display_data:
        st.info("No comments yet. Be the first to start the conversation!")
    else:
        # Show newest comments at the top
        for c in reversed(display_data):
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #F39C12;">
                    <strong style="color: #F39C12;">{c['name']}</strong> <small style="color: #888;">({c['time']})</small><br>
                    <p style="margin-top: 5px; color: white; line-height: 1.6;">{c['text']}</p>
                </div>
            """, unsafe_allow_html=True)
            
