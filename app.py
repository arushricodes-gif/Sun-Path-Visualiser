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
visuals.apply_styles()

# ── GPS / SESSION STATE INIT ──────────────────────────────────────────────────
if 'coords' not in st.session_state:
    st.session_state.coords      = [0.0, 0.0]
    st.session_state.gps_requested = False

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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        @font-face { font-family:'Akira'; src:url('https://fonts.cdnfonts.com/s/62983/Akira Expanded Demo.woff'); }
        html,body,[class*="st-at"],[class*="st-ae"] { font-family:'Poppins',sans-serif !important; }
        .flowstate-title {
            font-family:'Akira',sans-serif; font-size:80px; font-weight:900; color:#F39C12;
            text-align:center; text-transform:uppercase; letter-spacing:15px; line-height:1.1;
            margin-bottom:10px;
            background:linear-gradient(180deg,#F39C12 0%,#FFD06D 50%,#D35400 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            filter:drop-shadow(0px 0px 20px rgba(243,156,18,0.4));
        }
        .flowstate-subtitle {
            font-family:'Poppins',sans-serif; color:#F39C12; text-align:center;
            font-size:1.2rem; font-weight:300; letter-spacing:4px; text-transform:uppercase;
            margin-top:-20px; margin-bottom:40px;
        }
        </style>
        <h1 class="flowstate-title">SUN<br>SCOUT</h1>
        <p class="flowstate-subtitle">Visualize the Light</p>
    """, unsafe_allow_html=True)

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
        font_color="black",
        xaxis=dict(showgrid=False, color="black"),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', title="Elevation (°)", color="black")
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


# ── TABS ──────────────────────────────────────────────────────────────────────
tab_info, tab1, tab2, tab_summary = st.tabs([
    "Getting Started",
    "Step 1: 📍 Location Setup",
    "Step 2: 🚀 Live Visualization",
    "🔄 Year Round Summary",
    
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — INFO & HELP (STYLIZED)
# ══════════════════════════════════════════════════════════════════════════════
with tab_info: 
    st.markdown("""
    <style>
        .info-card {
            background: rgba(20, 24, 32, 0.5);
            border: 1px solid rgba(243, 156, 18, 0.15);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            font-family: 'Inter', sans-serif;
        }
        .info-header {
            font-family: 'Bebas Neue', sans-serif;
            color: #F39C12;
            font-size: 2rem;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .info-sub {
            font-family: 'JetBrains Mono', monospace;
            color: #9CA3AF;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
        }
        .highlight { color: #F39C12; font-weight: 600; }
        .code-font { font-family: 'JetBrains Mono', monospace; color: #E67E22; }
    </style>

    <div class="info-card">
        <div class="info-header">☀️ WELCOME TO SUN SCOUT</div>
        <div class="info-sub">Your Guide to Visualizing the Light</div>
        <p>This tool helps you "see" the sun's journey across the sky. Whether you're planning a garden, buying a house, or setting up solar panels, we translate complex celestial mechanics into simple, visual insights.</p>
    </div>

    <div class="info-card">
        <div class="info-header">UNDERSTANDING THE VIEWS</div>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin-bottom: 15px;"><span class="highlight">2D Map:</span> Think of this as your "top-down" blueprint. It shows exactly where the sun rises (<span style="color:#E74C3C;">Red</span>) and sets (<span style="color:#3498DB;">Blue</span>) for your specific location.</li>
            <li style="margin-bottom: 15px;"><span class="highlight">3D Arc:</span> This shows the sun's "rollercoaster" path. A high arc means long summer days; a low, flat arc means shorter winter days.</li>
            <li style="margin-bottom: 15px;"><span class="highlight">3D Shadow:</span> Our most powerful tool. It uses real building data to show exactly where shadows fall on your street at any hour.</li>
        </ul>
    </div>

    <div class="info-card">
        <div class="info-header">THE DATA DASHBOARD</div>
        <p>What do these technical terms actually mean for you?</p>
        <table style="width:100%; border-collapse: collapse; font-size: 0.9rem;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 10px; color: #F39C12;"><b>Azimuth</b></td>
                <td style="padding: 10px; color: #9CA3AF;">The compass direction of the sun (e.g., North is 0°, East is 90°).</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 10px; color: #F39C12;"><b>Elevation</b></td>
                <td style="padding: 10px; color: #9CA3AF;">How high the sun is. 0° is the horizon; 90° is directly overhead.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 10px; color: #F39C12;"><b>Solar Noon</b></td>
                <td style="padding: 10px; color: #9CA3AF;">The peak of the day—when the sun is at its highest point.</td>
            </tr>
            <tr>
                <td style="padding: 10px; color: #F39C12;"><b>Radiation</b></td>
                <td style="padding: 10px; color: #9CA3AF;">The "strength" of the sunlight ($W/m^2$). Higher is better for solar panels.</td>
            </tr>
        </table>
    </div>

    <div class="info-card" style="border-left: 4px solid #F39C12;">
        <div class="info-header" style="font-size: 1.2rem;">ACCURACY & DATA</div>
        <p style="font-size: 0.85rem; color: #9CA3AF;">
            Sun Scout uses the <span class="code-font">Astral</span> scientific library for solar math and <span class="code-font">OpenStreetMap</span> for building geometry. 
            While highly precise, please note that local obstacles like small trees or temporary fences might not appear in the 3D view.
        </p>
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

    # ── Map style toggle ──────────────────────────────────────────────────────
    st.markdown("""
    <style>
        .info-card {
            background: rgba(20, 24, 32, 0.5);
            border: 1px solid rgba(243, 156, 18, 0.15);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            font-family: 'Inter', sans-serif;
        }
        .info-header {
            font-family: 'Bebas Neue', sans-serif;
            color: #F39C12;
            font-size: 2rem;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .info-sub {
            font-family: 'JetBrains Mono', monospace;
            color: #9CA3AF;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
        }
        .highlight { color: #F39C12; font-weight: 600; }
        .code-font { font-family: 'JetBrains Mono', monospace; color: #E67E22; }
    </style>

    <div class="info-card">
        <div class="info-sub">What to do here?</div>
        <p>Select your location on the 2D Map. Also select the date and time. View your location on the 3D map. Then switch the "Step 2" to see the sun path, and the shadows. </p>
    </div>
    """, unsafe_allow_html=True)

    loc_view = st.radio("Map Style", ["🗺️ 2D Map", "🏙️ 3D Buildings"],
                        horizontal=True, key="loc_map_style")

    if loc_view == "🏙️ 3D Buildings":
        _path_data = build_path_data()
        _m_slat, _m_slon, _m_shlat, _m_shlon, _m_az, _m_el = solarlogic.get_solar_pos(
            city_info, sim_time, radius_meters, lat, lon)

        # Inject a postMessage receiver into the Streamlit parent page.
        # When the OSM Buildings iframe fires window.parent.postMessage({type:'osm_pin',...}),
        # this script writes the coords into a hidden input field which we read via
        # st.query_params on the next rerun.
        st.components.v1.html("""
        <script>
        window.addEventListener('message', function(e) {
            if (!e.data || e.data.type !== 'osm_pin') return;
            // Write into Streamlit query params so Python can read it
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
            allow_location_select=True
        )

        # Read pin from query params (set by JS above on previous click)
        qp = st.query_params
        if "pin_lat" in qp and "pin_lon" in qp:
            try:
                new_pin = [float(qp["pin_lat"]), float(qp["pin_lon"])]
                if new_pin != st.session_state.coords:
                    st.session_state.coords = new_pin
                    # Clear the query params so we don't re-apply on next render
                    st.query_params.clear()
                    st.rerun()
            except (ValueError, TypeError):
                pass

        st.info("View your location on the 3d map.")

    else:
        # ── 2D Folium map ─────────────────────────────────────────────────────
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
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"))

    elif view_mode == "🛰️ 3D Shadow":
        visuals.render_3d_shadow_component(
            lat, lon, radius_meters, path_data, animate_trigger, sim_time,
            m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
            rise_t.strftime("%H:%M"), set_t.strftime("%H:%M"))

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
    st.markdown('<div class="theory-section"><h2 class="theory-header">Seasonal Comparison For Selected Location</h2></div>',
                unsafe_allow_html=True)

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

    st.markdown("""
    <div style="display:flex; justify-content:space-around; background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-top:10px;">
        <div style="color:#FF4444;">&#9679; Summer</div>
        <div style="color:#FF8C00;">&#9679; Autumn</div>
        <div style="color:#F1C40F;">&#9679; Spring</div>
        <div style="color:#A8D8EA;">&#9679; Winter</div>
    </div>
    """, unsafe_allow_html=True)
