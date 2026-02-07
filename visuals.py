import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

def apply_styles():
    st.markdown("""
        <style>
        .stApp { background: #0b0f19; }
        .main-title { 
            color: #ffffff !important; 
            font-weight: 800; text-align: center; letter-spacing: 3px; padding: 20px 0;
            text-shadow: 0px 0px 15px rgba(255, 255, 255, 0.3); opacity: 1 !important; 
        }
        .obs-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; border-radius: 15px; height: 100%; }
        .sun-card { background: rgba(23, 33, 54, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; color: #72aee6; font-weight: 500; }
        .stTabs [aria-selected="true"] { color: #e74c3c !important; border-bottom-color: #e74c3c !important; }
        </style>
    """, unsafe_allow_html=True)

def render_map_component(lat, lon, radius_meters, path_data, animate_trigger, sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, rise_edge, set_edge):
    map_html = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map2" style="height: 700px; width: 100%; border-radius: 12px; border: 1px solid #444;"></div>
        <script>
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ noWrap: true }});
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ noWrap: true }});
            
            var map2 = L.map('map2', {{ 
                center: [{lat}, {lon}], 
                zoom: 17, 
                layers: [street],
                minZoom: 2
            }});
            
            L.control.layers({{"Street": street, "Satellite": satellite}}, null, {{collapsed: false}}).addTo(map2);
            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'white', weight: 1, fillOpacity: 0.1}}).addTo(map2);var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {rise_edge}], {{color: '#e74c3c', weight: 3}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {set_edge}], {{color: '#3498db', weight: 3}}).addTo(map2);
            var sunIcon = L.divIcon({{ html: '<div class="sun-emoji">☀️</div>', iconSize: [50, 50], iconAnchor: [25, 25], className: 'custom-sun-icon' }});
            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadowLine = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);
            function updateFrame(pos) {{
                if (pos && pos.el > -0.5) {{
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadowLine.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                }}
            }}
            if ({str(animate_trigger).lower()}) {{
                var i = 0;
                function doAnimate() {{ updateFrame(pathData[i]); i = (i + 1) % pathData.length; setTimeout(doAnimate, 100); }}
                doAnimate();
            }} else {{ updateFrame({{lat: {m_slat}, lon: {m_slon}, shlat: {m_shlat}, shlon: {m_shlon}, el: {m_el}}}); }}
        </script>
        <style>.sun-emoji {{ font-size: 32pt; }}</style>
    """
    components.html(map_html, height=700)
    
