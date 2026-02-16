import streamlit as st
import streamlit.components.v1 as components

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* Force Global Dark Background */
        .stApp {
            background-color: #0E1117 !important;
        }

        /* Fix Main Title */
        .main-title { 
            color: #F39C12 !important; 
            font-weight: 800 !important;
            text-align: center !important;
            margin: 0px auto !important;
            padding: 20px 0px !important;
            display: block !important;
            font-size: 2.5rem !important;
        }

        /* Fix Input Fields (Search box, Date picker) */
        /* This ensures the text isn't white-on-white */
        [data-baseweb="input"], [data-baseweb="base-input"] {
            background-color: #1A1C24 !important;
            border-radius: 8px !important;
        }
        
        input {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        /* Fix White-on-White Buttons (Search & Reset) */
        button[kind="secondaryFormSubmit"], 
        button[kind="secondary"], 
        [data-testid="stForm"] button {
            background-color: #F39C12 !important; 
            color: #FFFFFF !important; 
            border: none !important;
            font-weight: 700 !important;
        }
        
        /* Ensure Sidebar text and labels are visible */
        [data-testid="stSidebar"] {
            background-color: #0E1117 !important;
        }
        
        [data-testid="stWidgetLabel"] p, .stMarkdown p, label {
            color: #FFFFFF !important;
        }

        /* Fix Slider appearance */
        .stSlider [role="slider"] {
            background-color: #F39C12 !important;
        }

        /* Tab visibility fix */
        button[data-baseweb="tab"] { color: white !important; }
        button[aria-selected="true"] { 
            color: #F39C12 !important; 
            border-bottom-color: #F39C12 !important; 

        }
        /* Target all headers specifically to override the grey */
        h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] h2 {
            color: #FFFFFF !important;
        }

        /* Fix for the specific 'Seasonal Comparison' style header */
        .theory-header, .main-title {
            color: #F39C12 !important; /* Keep your gold color for main titles */
        }

        /* Ensure standard markdown text isn't inherited as grey */
        .stMarkdown p {
            color: #FFFFFF !important;
        }
        
        /* Fix for the date icon next to headers if it appears grey */
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0);
            color: white !important;
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
    
