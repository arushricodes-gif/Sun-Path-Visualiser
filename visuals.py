import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from datetime import timedelta

def apply_styles():
    st.markdown("""
        <style>
        .stApp { background: #0b0f19; }
        
        .main-title { 
            color: #ffffff !important; 
            font-weight: 800; 
            text-align: center; 
            letter-spacing: 3px; 
            padding: 20px 0;
            text-shadow: 0px 0px 15px rgba(255, 255, 255, 0.3);
            opacity: 1 !important; 
        } /* Added the missing closing bracket here */

        .obs-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; border-radius: 15px; height: 100%; }
        .sun-card { background: rgba(23, 33, 54, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; color: #72aee6; font-weight: 500; }
        .theory-section { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1); color: #ccc; }
        .theory-header { color: #F7DF88; font-weight: 700; margin-bottom: 15px; }
        .milestone-card { background: rgba(255, 255, 255, 0.05); border-left: 4px solid #f39c12; padding: 15px; margin-bottom: 10px; border-radius: 0 10px 10px 0; }
        [data-testid="stMetricValue"] { color: #f39c12 !important; font-weight: bold; }
        div[data-testid="metric-container"] { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; }
        .stTabs [aria-selected="true"] { color: #e74c3c !important; border-bottom-color: #e74c3c !important; }
        </style>
    """, unsafe_allow_html=True)

def render_map_component(lat, lon, radius_meters, path_data, animate_trigger, sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, rise_edge, set_edge):
    map_html = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map2" style="height: 1000px; width: 100%; border-radius: 12px; border: 1px solid #444;"></div>
        <script>
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var map2 = L.map('map2', {{ center: [{lat}, {lon}], zoom: 17, layers: [satellite] }});
            L.control.layers({{"Satellite": satellite, "Street": street}}, null, {{collapsed: false}}).addTo(map2);
            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'white', weight: 1, fillOpacity: 0.1}}).addTo(map2);
            L.marker([{lat}, {lon}]).addTo(map2);
            var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5, opacity: 0.8}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {rise_edge}], {{color: '#e74c3c', weight: 3}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {set_edge}], {{color: '#3498db', weight: 3}}).addTo(map2);
            var sunIcon = L.divIcon({{
                html: '<div class="sun-container"><div id="sun-time" class="sun-label"></div><div class="sun-emoji">☀️</div></div>', 
                iconSize: [100, 100], iconAnchor: [50, 50], className: 'custom-sun-icon'
            }});
            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadowLine = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);
            function updateFrame(pos) {{
                if (pos && pos.el > -0.5) {{
                    sunMarker.setOpacity(1); shadowLine.setStyle({{opacity: 0.5}});
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadowLine.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                    document.getElementById('sun-time').innerHTML = pos.time;
                }} else {{ sunMarker.setOpacity(0); shadowLine.setStyle({{opacity: 0}}); }}
            }}
            if ({str(animate_trigger).lower()}) {{
                var i = 0;
                function doAnimate() {{ updateFrame(pathData[i]); i = (i + 1) % pathData.length; setTimeout(doAnimate, 100); }}
                doAnimate();
            }} else {{ updateFrame({{lat: {m_slat}, lon: {m_slon}, shlat: {m_shlat}, shlon: {m_shlon}, time: "{sim_time.strftime('%H:%M')}", el: {m_el}}}); }}
        </script>
        <style>
            .custom-sun-icon {{ background: none !important; border: none !important; }}
            .sun-container {{ display: flex; position: relative; align-items: center; justify-content: center; width: 100px; height: 100px; }}
            .sun-label {{ background: rgba(0,0,0,0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10pt; position: absolute; top: 0px; border: 1px solid #f39c12; font-family: sans-serif; white-space: nowrap; }}
            .sun-emoji {{ font-size: 32pt; }}
        </style>
    """
    components.html(map_html, height=1000)
