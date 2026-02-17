import streamlit as st
import streamlit.components.v1 as components

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        /* 1. FORCE GLOBAL DARK THEME */
        .stApp { background-color: #0E1117 !important; }
        [data-testid="stSidebar"] { background-color: #000000 !important; }

        /* 2. FIX SEARCH BAR & INPUT BOXES */
        /* Make background light grey and TEXT PURE BLACK */
        [data-baseweb="input"], [data-baseweb="select"] > div {
            background-color: #D1D5DB !important; 
            border-radius: 8px !important;
            border: none !important;
        }
        
        /* This is the critical fix for invisible text */
        input {
            color: #000000 !important;
            font-weight: 500 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* 3. FIX THE "GHOST" BUTTONS (Search & Reset) */
        /* We target all buttons in the sidebar to be Orange */
        [data-testid="stSidebar"] button {
            background-color: #F39C12 !important;
            color: #FFFFFF !important;
            border: none !important;
            width: 100% !important;
            height: 3em !important;
            transition: 0.3s !important;
        }
        
        /* Force button text to be white, bold, and visible */
        [data-testid="stSidebar"] button p, [data-testid="stSidebar"] button div {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        
        /* Hover state so it doesn't turn white when touched */
        [data-testid="stSidebar"] button:hover {
            background-color: #e68a00 !important;
            border: none !important;
        }

        /* 4. FIX GREY/DIMMED LABELS */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #FFFFFF !important;
        }
        [data-testid="stWidgetLabel"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* 5. TABS STYLING */
        button[data-baseweb="tab"] p {
            color: #FFFFFF !important;
        }
        button[aria-selected="true"] {
            border-bottom-color: #F39C12 !important;
        }
        button[aria-selected="true"] p {
            color: #F39C12 !important;
        }

        /* 6. SLIDERS */
        .stSlider [data-baseweb="slider"] > div > div {
            background: #F39C12 !important;
        }

        .main-title { color: #F39C12 !important; font-weight: 800; text-align: center; padding: 20px 0px; font-size: 2.5rem; }
        </style>
    """, unsafe_allow_html=True)


def render_map_component(lat, lon, radius_meters, path_data, animate_trigger, sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, rise_edge, set_edge, rise_time, set_time, aqi_val):
    env = st.session_state.env_data
    wind_js = ""
    # Only render wind arrow if data exists and toggle is ON
    if env.get("wind_dir") is not None and aqi_val != "Off":
        wd = env["wind_dir"]
        wn = env["wind_name"].upper()
        # Calculate a small 100m arrow pointing FROM the wind direction TO the center
        wind_js = f"""
            var windRad = (({wd} + 180) * Math.PI) / 180;
            var sLat = {lat} - ((150/111111) * Math.cos(windRad));
            var sLon = {lon} - ((150/(111111 * Math.cos({lat} * Math.PI/180))) * Math.sin(windRad));
            var eLat = {lat} + ((30/111111) * Math.cos(windRad));
            var eLon = {lon} + ((30/(111111 * Math.cos({lat} * Math.PI/180))) * Math.sin(windRad));
            
            L.polyline([[sLat, sLon], [eLat, eLon]], {{color: '#00d2ff', weight: 4, opacity: 0.8}}).addTo(map2);
            L.marker([eLat, eLon], {{
                icon: L.divIcon({{
                    className: 'wind-arrow-container',
                    html: `<div style="transform: rotate({wd + 180}deg); color: #00d2ff; font-size: 20px;">▲</div>
                           <div style="color:#00d2ff; font-weight:800; text-shadow: 1px 1px 2px #000; font-size:11px; margin-left:25px; margin-top:-22px; white-space:nowrap;">{wn}</div>`,
                    iconSize: [20, 20], iconAnchor: [10, 10]
                }})
            }}).addTo(map2);
        """

    map_html = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map2" style="height: 700px; width: 100%; border-radius: 15px; border: 1px solid #333;"></div>
        <script>
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var map2 = L.map('map2', {{ center: [{lat}, {lon}], zoom: 17, layers: [street], zoomControl: false }});
            L.control.layers({{"Street": street, "Satellite": satellite}}, null, {{collapsed: false, position: 'topleft'}}).addTo(map2);
            
            var info = L.control({{position: 'topright'}});
            info.onAdd = function() {{
                var div = L.DomUtil.create('div', 'map-stats-card');
                div.innerHTML = `<div>🌅Sunrise: <b>{rise_time}</b></div><div>🌇Sunset: <b>{set_time}</b></div><div style="color:#F39C12;">💨 AQI: <b>{aqi_val}</b></div>`;
                return div;
            }};
            info.addTo(map2);

            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'black', weight: 4, fillOpacity: 0.1}}).addTo(map2);
            {wind_js}

            var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5, dashArray: '5, 10', opacity: 0.6}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {rise_edge}], {{color: '#e74c3c', weight: 5}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {set_edge}], {{color: '#3498db', weight: 5}}).addTo(map2);

            var sunIcon = L.divIcon({{ html: `<div class="sun-container"><div id="sun-time-label" class="pointing-box">--:--</div><div class="sun-emoji">☀️</div></div>`, iconSize: [80, 80], iconAnchor: [40, 62], className: 'custom-sun-icon' }});
            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadow = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);

            function update(pos) {{
                if (pos) {{
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadow.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                    document.getElementById('sun-time-label').innerHTML = pos.time;
                    sunMarker.setOpacity(pos.el < 0 ? 0 : 1);
                    shadow.setStyle({{opacity: pos.el < 0 ? 0 : 0.5}});
                }}
            }}
            if ({str(animate_trigger).lower()}) {{
                var i = 0; setInterval(() => {{ update(pathData[i]); i = (i + 1) % pathData.length; }}, 150);
            }} else {{ update({{lat:{m_slat}, lon:{m_slon}, shlat:{m_shlat}, shlon:{m_shlon}, el:{m_el}, time:"{sim_time.strftime('%H:%M')}"}}); }}
        </script>
        <style>
            .map-stats-card {{ background: rgba(14, 17, 23, 0.85); padding: 12px; border-radius: 12px; border: 1px solid #F39C12; color: white; font-size: 13px; }}
            .custom-sun-icon, .wind-arrow-container {{ background: none; border: none; }}
            .pointing-box {{ background: #F39C12; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
            .sun-emoji {{ font-size: 32pt; }}
        </style>
    """
    components.html(map_html, height=720)

def render_seasonal_map(lat, lon, radius, seasonal_paths):
    paths_js = ""
    color_map = {"Summer": "#FF0000", "Autumn": "#FF8C00", "Spring": "#FFD700", "Winter": "#FFFF00"}
    
    for season_id, data in seasonal_paths.items():
        coords, label = data["coords"], data["label"]
        if coords:
            color = color_map.get(season_id, '#FFF')
            
            # 1. Draw the Path Line
            paths_js += f"L.polyline({coords}, {{color: '{color}', weight: 6, opacity: 0.8}}).addTo(map_s);"
            
            # 2. Sunrise Circle + Permanent Label (Season Name)
            paths_js += f"""
                L.circleMarker({coords[0]}, {{radius: 7, color: 'white', weight: 2, fillColor: '{color}', fillOpacity: 1}}).addTo(map_s)
                 .bindTooltip('<b style="color:{color};">{season_id}</b>', {{permanent: true, direction: 'top', className: 'season-label'}});
            """
            
            # 3. Sunset Circle
            paths_js += f"L.circleMarker({coords[-1]}, {{radius: 7, color: 'white', weight: 2, fillColor: '{color}', fillOpacity: 1}}).addTo(map_s);"

    html_content = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map_s" style="height: 600px; width: 100%; border-radius: 15px; background: #111; border: 1px solid #444;"></div>
        <script>
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var map_s = L.map('map_s', {{ center: [{lat}, {lon}], zoom: 17, layers: [satellite], zoomControl: false }});
            
            L.control.zoom({{ position: 'bottomright' }}).addTo(map_s);
            L.control.layers({{"Satellite": satellite, "Street": street}}, null, {{position: 'topleft'}}).addTo(map_s);
            
            // Center location marker
            L.circle([{lat}, {lon}], {{ radius: {radius}, color: 'black', weight: 3, fillOpacity: 0.05 }}).addTo(map_s);
            L.circleMarker([{lat}, {lon}], {{radius: 5, color: 'white', fillColor: '#F39C12', fillOpacity: 1}}).addTo(map_s);
            
            {paths_js}
        </script>
        <style>
            /* Styling the permanent labels */
            .season-label {{
                background: rgba(0, 0, 0, 0.7) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                box-shadow: none !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: bold !important;
                font-size: 12px !important;
                padding: 2px 6px !important;
            }}
            /* Remove the little arrow from the tooltip */
            .leaflet-tooltip-top:before, .leaflet-tooltip-bottom:before {{
                display: none !important;
            }}
        </style>
    """
    st.components.v1.html(html_content, height=620)
    
