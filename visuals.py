import streamlit as st
import streamlit.components.v1 as components

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
        .theory-section { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; }
        .theory-header { color: #F7DF88; font-weight: 700; margin-bottom: 15px; }
        .milestone-card { background: rgba(255, 255, 255, 0.05); border-left: 4px solid #f39c12; padding: 15px; margin-bottom: 10px; border-radius: 0 10px 10px 0; }
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
            
            var map2 = L.map('map2', {{ center: [{lat}, {lon}], zoom: 17, layers: [street], minZoom: 2 }});
            
            L.control.layers({{"Street": street, "Satellite": satellite}}, null, {{collapsed: false}}).addTo(map2);
            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'white', weight: 1, fillOpacity: 0.1}}).addTo(map2);
            
            var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: 'orange', weight: 5, dashArray: '5, 10', opacity: 0.6}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {rise_edge}], {{color: '#e74c3c', weight: 3}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {set_edge}], {{color: '#3498db', weight: 3}}).addTo(map2);

            // --- FIXED SUN ICON WITH POINTING BOX ---
            var sunIcon = L.divIcon({{ 
                html: `
                    <div class="sun-container">
                        <div id="sun-time-label" class="pointing-box">--:--</div>
                        <div class="sun-emoji">☀️</div>
                    </div>
                `, 
                iconSize: [80, 80], 
                iconAnchor: [40, 62], 
                className: 'custom-sun-icon' 
            }});

            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadowLine = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: 'grey', weight: 5, opacity: 0.5}}).addTo(map2);

            function updateFrame(pos) {{
                if (pos) {{
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadowLine.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                    
                    var label = document.getElementById('sun-time-label');
                    if(label) label.innerHTML = pos.time;
                    
                    if (pos.el < 0) {{
                        sunMarker.setOpacity(0);
                        shadowLine.setStyle({{opacity: 0}});
                    }} else {{
                        sunMarker.setOpacity(1);
                        shadowLine.setStyle({{opacity: 0.5}});
                    }}
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
                updateFrame({{
                    lat: {m_slat}, 
                    lon: {m_slon}, 
                    shlat: {m_shlat}, 
                    shlon: {m_shlon}, 
                    el: {m_el}, 
                    time: "{sim_time.strftime('%H:%M')}"
                }}); 
            }}
        </script>
        <style>
            .custom-sun-icon {{ background: none; border: none; }}
            
            .sun-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 80px;
                height: 80px;
                justify-content: center; /* Pushes emoji to the bottom */
            }}

            .pointing-box {{
                position: relative;
                background: #f39c12;
                color: #0b0f19;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                font-family: sans-serif;
                font-size: 14px;
                margin-bottom: 5px; /* Distance from sun emoji */
                box-shadow: 0 2px 5px rgba(0,0,0,0.5);
                white-space: nowrap;
            }}

            .pointing-box::after {{
                content: '';
                position: absolute;
                bottom: -6px;
                left: 50%;
                transform: translateX(-50%);
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #f39c12;
            }}

            .sun-emoji {{ 
                font-size: 32pt;
                line-height: 1; /* Prevents emoji shifting */
                margin: 0;
                padding: 0;
                display: block;
                filter: drop-shadow(0 0 10px rgba(243, 156, 18, 0.7));
            }}
        </style>
    """
    components.html(map_html, height=720)

def render_seasonal_map(lat, lon, radius, seasonal_paths):
    colors = {
        "Summer": "#FF0000", 
        "Autumn": "#FF8C00", 
        "Spring": "#FFD700", 
        "Winter": "#FFFF00"
    }
    
    paths_js = ""
    for season_id, data in seasonal_paths.items():
        coords = data["coords"]
        label = data["label"] # This is the "Season (Date)" string
        
        if coords:
            paths_js += f"""
            L.polyline({coords}, {{
                color: '{colors.get(season_id, "#FFFFFF")}', 
                weight: 6, 
                opacity: 0.8
            }}).addTo(map_s).bindTooltip('<b>{label}</b>', {{
                sticky: true, 
                className: 'custom-tooltip'
            }});
            """

    html_content = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            .custom-tooltip {{
                background-color: #333 !important;
                color: white !important;
                border: 1px solid #777 !important;
                font-family: sans-serif;
            }}
        </style>
        <div id="map_s" style="height: 600px; width: 100%; border-radius: 15px; background: #000;"></div>
        <script>
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');

            var map_s = L.map('map_s', {{
                center: [{lat}, {lon}],
                zoom: 17,
                layers: [satellite]
            }});

            L.control.layers({{"Satellite": satellite, "Street": street}}).addTo(map_s);
            
            // Black Sun Circle
            L.circle([{lat}, {lon}], {{
                radius: {radius}, 
                color: 'white', 
                weight: 1, 
                fillColor: 'black', 
                fillOpacity: 0.4
            }}).addTo(map_s);

            L.circle([{lat}, {lon}], {{radius: 2, color: 'white', fillOpacity: 1}}).addTo(map_s);
            
            {paths_js}
        </script>
    """
    st.components.v1.html(html_content, height=620)
    
