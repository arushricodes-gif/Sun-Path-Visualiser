import streamlit as st
import streamlit.components.v1 as components
import math


def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* 1. Global Backgrounds */
        .stApp { background-color: #0E1117 !important; }
        [data-testid="stSidebar"] { background-color: #000000 !important; }

        /* 2. SEARCH BAR */
        div[data-baseweb="input"] {
            background-color: #D1D5DB !important;
            border-radius: 8px !important;
        }
        input {
            color: #F39C12 !important;
            -webkit-text-fill-color: #F39C12 !important;
            font-weight: 700 !important;
        }
        input::placeholder {
            color: #444444 !important;
            -webkit-text-fill-color: #444444 !important;
        }

        /* 3. BUTTONS */
        button[kind="secondaryFormSubmit"], .stButton > button {
            background-color: #F39C12 !important;
            color: #FFFFFF !important;
            border: none !important;
            width: 100% !important;
            font-weight: 1000 !important;
            transition: 0.3s !important;
        }
        button[kind="secondaryFormSubmit"] p, .stButton > button p {
            color: #FFFFFF !important;
        }
        button[kind="secondaryFormSubmit"]:hover, .stButton > button:hover {
            background-color: #e68a00 !important;
            color: #FFFFFF !important;
        }
        .stButton > button p { color: #FFFFFF !important; font-weight: 800 !important; }
        .stButton > button:hover { background-color: #e68a00 !important; border: none !important; }

        /* 4. TABS & LABELS */
        h1, h2, h3, h4, h5, h6, p, span, label, [data-testid="stWidgetLabel"] p {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }
        button[aria-selected="true"] p { color: #F39C12 !important; }

        /* 5. SLIDERS */
        .stSlider [data-baseweb="slider"] > div > div { background: #F39C12 !important; }

        .main-title {
            color: #F39C12 !important; font-weight: 800;
            text-align: center; padding: 20px 0px; font-size: 2.5rem;
        }

        /* MOBILE */
        @media (max-width: 768px) {
            iframe { height: 450px !important; }
            .main .block-container { padding-bottom: 1rem !important; }
            [data-testid="stMetric"] { padding: 5px !important; }
        }

        div[data-testid="stHtml"] { margin-bottom: -30px !important; }
        </style>
    """, unsafe_allow_html=True)


def render_map_component(lat, lon, radius_meters, path_data, animate_trigger,
                          sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el,
                          rise_edge, set_edge, rise_time, set_time, aqi_val):
    env = st.session_state.env_data
    wind_js = ""
    if env.get("wind_dir") is not None and aqi_val != "Off":
        wd = env["wind_dir"]
        wn = env["wind_name"].upper()
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
        <div id="map2" style="height: 550px; width: 95%; border-radius: 15px; border: 1px solid #333;"></div>
        <script>
            var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var map2 = L.map('map2', {{ center: [{lat}, {lon}], zoom: 17, layers: [street], zoomControl: false }});
            L.control.layers({{"Street": street, "Satellite": satellite}}, null, {{collapsed: false, position: 'topleft'}}).addTo(map2);

            var info = L.control({{position: 'topright'}});
            info.onAdd = function() {{
                var div = L.DomUtil.create('div', 'map-stats-card');
                div.innerHTML = `<div>🌅Sunrise: <b>{rise_time}</b></div><div>🌇Sunset: <b>{set_time}</b></div><div style="color:#F39C12;">💨 AQI: <b>{aqi_val}</b></div><div>LEGEND:</div><div>🔴 Sunrise Line</div><div>🔵 Sunset Line</div><div>⚪ Shadow Line</div>`;
                return div;
            }};
            info.addTo(map2);

            L.circle([{lat}, {lon}], {{radius: {radius_meters}, color: 'black', weight: 4, fillOpacity: 0.1}}).addTo(map2);
            {wind_js}

            var pathData = {path_data};
            L.polyline(pathData.map(p => [p.lat, p.lon]), {{color: '#FF7518', weight: 7, dashArray: '5, 10', opacity: 0.6}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {rise_edge}], {{color: '#e74c3c', weight: 5}}).addTo(map2);
            L.polyline([[{lat}, {lon}], {set_edge}],  {{color: '#3498db', weight: 5}}).addTo(map2);

            var sunIcon = L.divIcon({{ html: `<div class="sun-container"><div id="sun-time-label" class="pointing-box">--:--</div><div class="sun-emoji">☀️</div></div>`, iconSize: [80, 80], iconAnchor: [40, 62], className: 'custom-sun-icon' }});
            var sunMarker = L.marker([0, 0], {{icon: sunIcon}}).addTo(map2);
            var shadow = L.polyline([[{lat}, {lon}], [{lat}, {lon}]], {{color: '#4F4F4F', weight: 6, opacity: 0.8}}).addTo(map2);

            function update(pos) {{
                if (pos) {{
                    sunMarker.setLatLng([pos.lat, pos.lon]);
                    shadow.setLatLngs([[{lat}, {lon}], [pos.shlat, pos.shlon]]);
                    document.getElementById('sun-time-label').innerHTML = pos.time;
                    sunMarker.setOpacity(pos.el < 0 ? 0 : 1);
                    shadow.setStyle({{opacity: pos.el < 0 ? 0 : 0.8}});
                }}
            }}
            if ({str(animate_trigger).lower()}) {{
                var i = 0; setInterval(() => {{ update(pathData[i]); i = (i + 1) % pathData.length; }}, 150);
            }} else {{
                update({{lat:{m_slat}, lon:{m_slon}, shlat:{m_shlat}, shlon:{m_shlon}, el:{m_el}, time:"{sim_time.strftime('%H:%M')}"}});
            }}
        </script>
        <style>
            .map-stats-card {{ background: rgba(14,17,23,0.85); padding: 12px; border-radius: 12px; border: 1px solid #F39C12; color: white; font-size: 13px; }}
            .custom-sun-icon, .wind-arrow-container {{ background: none; border: none; }}
            .pointing-box {{ background: #F39C12; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
            .sun-emoji {{ font-size: 32pt; }}
        </style>
    """
    components.html(map_html, height=550)


def render_seasonal_map(lat, lon, radius, seasonal_paths):
    paths_js = ""
    color_map = {"Summer": "#FF0000", "Autumn": "#FF8C00", "Spring": "#FFD700", "Winter": "#FFFF00"}

    for season_id, data in seasonal_paths.items():
        coords, label = data["coords"], data["label"]
        if coords:
            color = color_map.get(season_id, '#FFF')
            paths_js += f"L.polyline({coords}, {{color: '{color}', weight: 6, opacity: 0.8}}).addTo(map_s);"
            paths_js += f"""
                L.circleMarker({coords[0]}, {{radius: 7, color: 'white', weight: 2, fillColor: '{color}', fillOpacity: 1}}).addTo(map_s)
                 .bindTooltip('<b style="color:{color};">{season_id}</b>', {{permanent: true, direction: 'top', className: 'season-label'}});
            """
            paths_js += f"L.circleMarker({coords[-1]}, {{radius: 7, color: 'white', weight: 2, fillColor: '{color}', fillOpacity: 1}}).addTo(map_s);"

    set_coords  = [lat, lon - 0.0055]
    rise_coords = [lat, lon + 0.0035]

    html_content = f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="map_s" style="height: 600px; width: 100%; border-radius: 15px; background: #111; border: 1px solid #444;"></div>
        <script>
            var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
            var street    = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
            var map_s = L.map('map_s', {{ center: [{lat}, {lon}], zoom: 17, layers: [satellite], zoomControl: false }});
            L.control.zoom({{ position: 'bottomright' }}).addTo(map_s);
            L.control.layers({{"Satellite": satellite, "Street": street}}, null, {{position: 'topleft'}}).addTo(map_s);
            L.circle([{lat}, {lon}], {{ radius: {radius}, color: 'black', weight: 3, fillOpacity: 0.05 }}).addTo(map_s);
            L.circleMarker([{lat}, {lon}], {{radius: 5, color: 'white', fillColor: '#F39C12', fillOpacity: 1}}).addTo(map_s);
            L.marker({set_coords},  {{ opacity: 0 }}).addTo(map_s).bindTooltip("SUNSET",  {{ permanent: true, direction: 'center', className: 'loc-label sunset-vibrant' }});
            L.marker({rise_coords}, {{ opacity: 0 }}).addTo(map_s).bindTooltip("SUNRISE", {{ permanent: true, direction: 'center', className: 'loc-label sunrise-vibrant' }});
            {paths_js}
        </script>
        <style>
            .season-label {{
                background: rgba(0,0,0,0.8) !important; border: 1px solid rgba(255,255,255,0.2) !important;
                color: white !important; font-family: 'Inter', sans-serif !important;
                font-weight: bold !important; font-size: 11px !important; padding: 2px 6px !important;
            }}
            .leaflet-tooltip-top:before {{ display: none !important; }}
            .loc-label {{
                background: transparent !important; border: none !important; box-shadow: none !important;
                font-family: 'Inter', sans-serif !important; font-weight: 900 !important;
                font-size: 38px !important; letter-spacing: 3px !important; pointer-events: none !important;
            }}
            .sunrise-vibrant {{ color: #FF0000 !important; text-shadow: 0 0 20px rgba(255,0,0,0.4), 2px 2px 5px #000 !important; }}
            .sunset-vibrant  {{ color: #0070FF !important; text-shadow: 0 0 20px rgba(0,112,255,0.4), 2px 2px 5px #000 !important; }}
        </style>
    """
    components.html(html_content, height=620)


def render_3d_map_component(lat, lon, radius_meters, path_data, animate_trigger,
                              sim_time, m_slat, m_slon, m_el, rise_time, set_time):
    cos_lat = math.cos(math.radians(lat))
    R = radius_meters

    pts = []
    for p in path_data:
        dx = (p["lon"] - lon) * 111111 * cos_lat
        dz = -(p["lat"] - lat) * 111111
        dy = max(0, p["el"]) * (R / 90.0) * 2.2
        pts.append({"x": round(dx, 2), "y": round(dy, 2), "z": round(dz, 2),
                    "el": round(p["el"], 2), "time": p["time"]})
    pts_js = str(pts).replace("'", '"').replace("True", "true").replace("False", "false")

    cur_x    = round((m_slon - lon) * 111111 * cos_lat, 2)
    cur_z    = round(-(m_slat - lat) * 111111, 2)
    cur_y    = round(max(0, m_el) * (R / 90.0) * 2.2, 2)
    cur_time = sim_time.strftime('%H:%M')
    cam_dist = int(R * 2.2)
    cam_h    = int(R * 1.3)

    html = f"""<!DOCTYPE html><html><head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0d14; overflow:hidden; font-family:'Inter',sans-serif; }}
canvas {{ display:block; width:100% !important; height:600px !important; }}
#hud {{
  position:absolute; top:14px; right:14px;
  background:rgba(14,17,23,0.90); border:1.5px solid #F39C12;
  border-radius:12px; padding:12px 16px; color:#fff;
  font-size:13px; min-width:155px; pointer-events:none; line-height:1.9;
}}
#hud b {{ color:#F39C12; }}
#sun-badge {{
  position:absolute; top:14px; left:14px;
  background:rgba(14,17,23,0.90); border:1.5px solid #F39C12;
  border-radius:8px; padding:8px 14px;
  color:#F39C12; font-size:15px; font-weight:800; pointer-events:none;
}}
#hint {{
  position:absolute; bottom:12px; left:50%; transform:translateX(-50%);
  color:rgba(255,255,255,0.35); font-size:11px; pointer-events:none;
}}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud">
  🌅 Sunrise: <b>{rise_time}</b><br>
  🌇 Sunset: <b>{set_time}</b><br>
  ☀️ Elevation: <b id="h-el">{m_el:.1f}°</b><br>
  🕐 Time: <b id="h-time">{cur_time}</b>
</div>
<div id="sun-badge">☀️ <span id="s-time">{cur_time}</span></div>
<div id="hint">🖱 Drag to orbit &nbsp;·&nbsp; Scroll to zoom</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const canvas = document.getElementById('c');
const W = canvas.parentElement ? canvas.parentElement.clientWidth : window.innerWidth;
const H = 600;
canvas.width = W; canvas.height = H;

const renderer = new THREE.WebGLRenderer({{canvas, antialias:true}});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0d14);
scene.fog = new THREE.FogExp2(0x0a0d14, 0.0008);

const camera = new THREE.PerspectiveCamera(50, W/H, 0.5, 8000);
camera.position.set({cam_dist}, {cam_h}, {cam_dist});
camera.lookAt(0,0,0);

scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const dl = new THREE.DirectionalLight(0xffd580, 1.4);
dl.position.set(300, 600, 300); dl.castShadow = true; scene.add(dl);

const R = {R};
const ground = new THREE.Mesh(
  new THREE.CylinderGeometry(R, R, 4, 80),
  new THREE.MeshLambertMaterial({{color: 0x1c2a18}})
);
ground.position.y = -2; ground.receiveShadow = true; scene.add(ground);
scene.add(new THREE.GridHelper(R * 2, Math.max(10, Math.round(R / 13)), 0x2a3a28, 0x1e2e1c));

scene.add(new THREE.Mesh(
  new THREE.TorusGeometry(R, 4, 8, 80),
  new THREE.MeshBasicMaterial({{color: 0x444444}})
));

const cM = new THREE.LineBasicMaterial({{color: 0x333333}});
scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-R,1,0), new THREE.Vector3(R,1,0)]), cM));
scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,1,-R), new THREE.Vector3(0,1,R)]), cM));

const pillar = new THREE.Mesh(new THREE.CylinderGeometry(7,7,22,16), new THREE.MeshLambertMaterial({{color:0xF39C12}}));
pillar.position.y = 11; scene.add(pillar);
const baseGlow = new THREE.Mesh(new THREE.TorusGeometry(14,3,8,32), new THREE.MeshBasicMaterial({{color:0xF39C12,transparent:true,opacity:0.5}}));
scene.add(baseGlow);

function makeSprite(text, color) {{
  const cv = document.createElement('canvas'); cv.width=128; cv.height=64;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = color; ctx.font = 'bold 40px sans-serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, 64, 32);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({{map: new THREE.CanvasTexture(cv), transparent:true, depthTest:false}}));
  sp.scale.set(55, 28, 1); return sp;
}}
const ld = R + 45;
[['N','#ff4444',0,-ld],['S','#aaaaaa',0,ld],['E','#aaaaaa',ld,0],['W','#aaaaaa',-ld,0]].forEach(([t,c,x,z])=>{{
  const sp = makeSprite(t, c); sp.position.set(x, 8, z); scene.add(sp);
}});

const pathData = {pts_js};
const arcPts = pathData.filter(p => p.el >= 0).map(p => new THREE.Vector3(p.x, p.y, p.z));
if (arcPts.length > 1) {{
  const curve = new THREE.CatmullRomCurve3(arcPts);
  scene.add(new THREE.Mesh(
    new THREE.TubeGeometry(curve, arcPts.length * 3, 3.5, 8, false),
    new THREE.MeshBasicMaterial({{color: 0xFF7518, transparent:true, opacity:0.85}})
  ));
}}

pathData.filter(p => p.el >= 0).forEach((p, i) => {{
  if (i % 3 !== 0) return;
  const col = new THREE.Color().setHSL(0.08 - (i/pathData.length)*0.05, 1.0, 0.55);
  const dot = new THREE.Mesh(new THREE.SphereGeometry(5,8,8), new THREE.MeshBasicMaterial({{color:col}}));
  dot.position.set(p.x, p.y, p.z); scene.add(dot);
}});

pathData.filter(p => p.el >= 0).forEach((p, i) => {{
  if (i % 6 !== 0) return;
  const lg = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(p.x,0,p.z), new THREE.Vector3(p.x,p.y,p.z)]);
  scene.add(new THREE.Line(lg, new THREE.LineBasicMaterial({{color:0x664400,transparent:true,opacity:0.35}})));
}});

const sunMesh  = new THREE.Mesh(new THREE.SphereGeometry(18,24,24), new THREE.MeshBasicMaterial({{color:0xFFD700}}));
const haloMesh = new THREE.Mesh(new THREE.SphereGeometry(28,24,24), new THREE.MeshBasicMaterial({{color:0xFF8800,transparent:true,opacity:0.20,side:THREE.BackSide}}));
scene.add(sunMesh); scene.add(haloMesh);

const shPts = [new THREE.Vector3(0,0,0), new THREE.Vector3(0,0,0)];
const shGeo = new THREE.BufferGeometry().setFromPoints(shPts);
const shadowLine = new THREE.Line(shGeo, new THREE.LineBasicMaterial({{color:0x888888,transparent:true,opacity:0.7}}));
scene.add(shadowLine);

function setSun(x, y, z, timeStr, elDeg) {{
  sunMesh.position.set(x, Math.max(0,y), z);
  haloMesh.position.set(x, Math.max(0,y), z);
  const sp = shGeo.attributes.position;
  sp.setXYZ(0, 0, 0.5, 0);
  sp.setXYZ(1, x === 0 ? 0 : -x*2, 0.5, z === 0 ? 0 : -z*2);
  sp.needsUpdate = true;
  document.getElementById('h-el').textContent  = elDeg.toFixed(1) + '°';
  document.getElementById('h-time').textContent = timeStr;
  document.getElementById('s-time').textContent = timeStr;
  sunMesh.visible  = elDeg >= -2;
  haloMesh.visible = elDeg >= -2;
}}
setSun({cur_x}, {cur_y}, {cur_z}, '{cur_time}', {m_el});

let animIdx = 0;
if ({'true' if animate_trigger else 'false'}) {{
  setInterval(() => {{
    const p = pathData[animIdx];
    setSun(p.x, p.y, p.z, p.time, p.el);
    animIdx = (animIdx + 1) % pathData.length;
  }}, 160);
}}

let drag = false, prev = {{x:0,y:0}}, theta = Math.PI/4, phi = Math.PI/3.5, camR = {int(cam_dist*1.3)};
function updateCam() {{
  camera.position.set(
    camR * Math.sin(phi) * Math.sin(theta),
    camR * Math.cos(phi),
    camR * Math.sin(phi) * Math.cos(theta)
  );
  camera.lookAt(0, 0, 0);
}}
updateCam();
canvas.addEventListener('mousedown', e => {{ drag=true; prev={{x:e.clientX,y:e.clientY}}; }});
canvas.addEventListener('mouseup',   () => drag=false);
canvas.addEventListener('mousemove', e => {{
  if (!drag) return;
  theta -= (e.clientX - prev.x) * 0.005;
  phi = Math.max(0.15, Math.min(Math.PI/2.1, phi + (e.clientY - prev.y) * 0.005));
  prev = {{x:e.clientX, y:e.clientY}}; updateCam();
}});
canvas.addEventListener('wheel', e => {{
  camR = Math.max(R*0.6, Math.min(R*4, camR + e.deltaY*0.4));
  updateCam(); e.preventDefault();
}}, {{passive:false}});
let lt = null;
canvas.addEventListener('touchstart', e => lt = e.touches[0]);
canvas.addEventListener('touchmove',  e => {{
  if (!lt) return;
  const t = e.touches[0];
  theta -= (t.clientX - lt.clientX) * 0.005;
  phi = Math.max(0.15, Math.min(Math.PI/2.1, phi + (t.clientY - lt.clientY) * 0.005));
  lt = t; updateCam(); e.preventDefault();
}}, {{passive:false}});

function loop() {{ requestAnimationFrame(loop); renderer.render(scene, camera); }}
loop();
</script></body></html>"""
    components.html(html, height=620)
