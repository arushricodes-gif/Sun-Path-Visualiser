import streamlit as st
import streamlit.components.v1 as components

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* 1. Force the Heading to Show and Center */
        .main-title { 
            color: #F39C12 !important; 
            font-weight: 800 !important;
            text-align: center !important;
            margin: 0px auto !important;
            padding: 20px 0px !important;
            display: block !important;
            font-size: 2.5rem !important;
            width: 100% !important;
            position: relative !important;
            z-index: 999 !important;
        }

        /* 2. Remove Streamlit's default top padding gap */
        .block-container {
            padding-top: 1rem !important;
        }

        /* 3. Fix Text Visibility (Forces White for Dark Mode) */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown, p, span, label, li {
            color: #FFFFFF !important; 
            font-family: 'Inter', sans-serif;
        }

        /* 3. Global Text Visibility (Force White) */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown, p, span, label, li {
            color: #FFFFFF !important; 
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
        }

        /* 4. Date & Slider Visibility Fix */
        [data-testid="stWidgetLabel"] p, .stSlider div { color: #FFFFFF !important; }
        [data-baseweb="input"] input, .stSlider [role="slider"] { 
            color: #F39C12 !important; 
            font-weight: bold !important;
        }

        /* 5. Info Tab Styling */
        .theory-section {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(243, 156, 18, 0.3);
            margin-bottom: 20px;
        }
        .theory-header { color: #F39C12 !important; font-weight: 800; }
        .milestone-card {
            background: #1A1C24;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #F39C12;
            margin-bottom: 10px;
        }
        
        /* 6. Legend/Line Index Styling */
        .legend-container {
            display: flex;
            justify-content: space-around;
            background: #1A1C24;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #333;
            margin-top: 10px;
        }
        .legend-item { font-weight: bold; font-size: 0.9rem; }

        /* 7. Sidebar & Buttons */
        [data-testid="stSidebar"] { background-color: #0E1117 !important; border-right: 1px solid #333; }
        button[kind="secondaryFormSubmit"], button[kind="secondary"], [data-testid="stForm"] button {
            background: #F39C12 !important; color: white !important; font-weight: 700 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_map_component(lat, lon, radius_meters, path_data, animate_trigger, sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, rise_edge, set_edge, rise_time, set_time, aqi_val):
    map_html = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map2" style="height: 700px; width: 100%; border-radius: 15px; border: 1px solid #333; position: relative;"></div>
        <script>
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var map2 = L.map('map2', {{ center: [{lat}, {lon}], zoom: 17, layers: [street], zoomControl: false }});
            
            L.control.zoom({{ position: 'bottomright' }}).addTo(map2);
            L.control.layers({{"Street": street, "Satellite": satellite}}, null, {{ collapsed: false, position: 'topleft' }}).addTo(map2);
            
            // --- CUSTOM MAP OVERLAY ---
            var infoControl = L.control({{position: 'topright'}});
            infoControl.onAdd = function (map) {{
                var div = L.DomUtil.create('div', 'map-stats-card');
                div.innerHTML = `
                    <div style="margin-bottom: 5px;">🌅Sunrise: <b>{rise_time}</b></div>
                    <div style="margin-bottom: 5px;">🌇Sunset: <b>{set_time}</b></div>
                    <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 5px; color: #F39C12;">💨 AQI: <b>{aqi_val}</b></div>
                `;
                return div;
            }};
            infoControl.addTo(map2);

            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'black', weight: 4, fillOpacity: 0.1}}).addTo(map2);
            var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5, dashArray: '5, 10', opacity: 0.6}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {rise_edge}], {{color: '#e74c3c', weight: 5}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {set_edge}], {{color: '#3498db', weight: 5}}).addTo(map2);

            var sunIcon = L.divIcon({{ 
                html: `<div class="sun-container"><div id="sun-time-label" class="pointing-box">--:--</div><div class="sun-emoji">☀️</div></div>`, 
                iconSize: [80, 80], iconAnchor: [40, 62], className: 'custom-sun-icon' 
            }});

            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadowLine = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);

            function updateFrame(pos) {{
                if (pos) {{
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadowLine.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                    document.getElementById('sun-time-label').innerHTML = pos.time;
                    sunMarker.setOpacity(pos.el < 0 ? 0 : 1);
                    shadowLine.setStyle({{opacity: pos.el < 0 ? 0 : 0.5}});
                }}
            }}

            if ({str(animate_trigger).lower()}) {{
                var i = 0; 
                function doAnimate() {{ 
                    updateFrame(pathData[i]); 
                    i = (i + 1) % pathData.length; 
                    setTimeout(doAnimate, 150); 
                }} 
                doAnimate();
            }} else {{ 
                updateFrame({{lat: {m_slat}, lon: {m_slon}, shlat: {m_shlat}, shlon: {m_shlon}, el: {m_el}, time: "{sim_time.strftime('%H:%M')}"}}); 
            }}
        </script>
        <style>
            .map-stats-card {{
                background: rgba(14, 17, 23, 0.85);
                backdrop-filter: blur(10px);
                padding: 12px 15px;
                border-radius: 12px;
                border: 1px solid rgba(243, 156, 18, 0.4);
                color: white;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                margin: 10px;
            }}
            .custom-sun-icon {{ background: none; border: none; }}
            .pointing-box {{ background: #F39C12; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }}
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
            paths_js += f"L.polyline({coords}, {{color: '{color_map.get(season_id, '#FFF')}', weight: 6, opacity: 0.8}}).addTo(map_s).bindTooltip('<b>{label}</b>', {{sticky: true}});"
    html_content = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map_s" style="height: 600px; width: 100%; border-radius: 15px; background: #111; border: 1px solid #444;"></div>
        <script>
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var map_s = L.map('map_s', {{ center: [{lat}, {lon}], zoom: 17, layers: [satellite] }});
            L.control.layers({{"Satellite": satellite, "Street": street}}).addTo(map_s);
            L.circle([{lat}, {lon}], {{ radius: {radius}, color: 'black', weight: 4, fillOpacity: 0.1 }}).addTo(map_s);
            L.circle([{lat}, {lon}], {{radius: 5, color: 'black', fillOpacity: 1}}).addTo(map_s);
            {paths_js}
        </script>
    """
    st.components.v1.html(html_content, height=620)
