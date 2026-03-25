import streamlit as st
import streamlit.components.v1 as components
import math


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --gold:  #F39C12;
        --gold2: #E67E22;
        --dim:   #A06808;
        --glow:  rgba(243,156,18,.15);
        --bg:    #0A0C10;
        --s1:    #0F1218;
        --s2:    #141820;
        --s3:    #1C2230;
        --b1:    rgba(255,255,255,.05);
        --b2:    rgba(255,255,255,.08);
        --b3:    rgba(243,156,18,.18);
        --t1:    #F0F2F5;
        --t2:    #9CA3AF;
        --t3:    #4B5563;
    }

    /* ── Base ── */
    .stApp {
        background: var(--bg) !important;
        background-image:
            radial-gradient(ellipse 100% 40% at 50% 0%, rgba(243,156,18,.055) 0%, transparent 65%) !important;
    }

    /* ── Fonts ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    h1, h2, h3 {
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: .04em !important;
        color: var(--t1) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #070910 !important;
        border-right: 1px solid rgba(243,156,18,.08) !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: var(--s1) !important;
        border: 1px solid var(--b1) !important;
        border-radius: 14px !important;
        padding: 5px !important;
        gap: 3px !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 10px !important;
        color: var(--t3) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 9px 20px !important;
        transition: all .2s !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: var(--glow) !important;
        color: var(--gold) !important;
        border: 1px solid var(--b3) !important;
    }
    [data-testid="stTabs"] button[role="tab"] p { color: inherit !important; }
    button[aria-selected="true"] p { color: var(--gold) !important; }

    /* ── Text inputs ── */
    div[data-baseweb="input"] {
        background: var(--s2) !important;
        border: 1px solid var(--b2) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: rgba(243,156,18,.35) !important;
        box-shadow: 0 0 0 3px rgba(243,156,18,.08) !important;
    }
    input {
        color: var(--gold) !important;
        -webkit-text-fill-color: var(--gold) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }
    input::placeholder {
        color: var(--t3) !important;
        -webkit-text-fill-color: var(--t3) !important;
    }

    /* ── Buttons ── */
    button[kind="secondaryFormSubmit"], .stButton > button {
        background: var(--gold) !important;
        color: #000 !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        letter-spacing: .04em !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        width: 100% !important;
        transition: all .2s !important;
        box-shadow: 0 4px 20px rgba(243,156,18,.2) !important;
        font-family: 'Inter', sans-serif !important;
    }
    button[kind="secondaryFormSubmit"] p, .stButton > button p {
        color: #000 !important; font-weight: 600 !important;
    }
    button[kind="secondaryFormSubmit"]:hover, .stButton > button:hover {
        background: #FFB020 !important;
        box-shadow: 0 6px 28px rgba(243,156,18,.35) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Sliders ── */
    .stSlider [data-baseweb="slider"] > div > div {
        background: linear-gradient(90deg, var(--dim), var(--gold)) !important;
        height: 3px !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--gold) !important;
        border: 2px solid #000 !important;
        box-shadow: 0 0 0 3px rgba(243,156,18,.25) !important;
        width: 15px !important; height: 15px !important;
    }
    [data-testid="stSliderTickBar"] { display: none !important; }
    [data-testid="stWidgetLabel"] p {
        font-size: 10px !important;
        letter-spacing: .1em !important;
        text-transform: uppercase !important;
        color: var(--t3) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ── Toggle ── */
    [data-testid="stToggle"] [data-checked="true"] { background: var(--gold) !important; }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        background: var(--s2) !important;
        border: 1px solid var(--b2) !important;
        border-radius: 10px !important;
        color: var(--t1) !important;
        font-size: 13px !important;
    }

    /* ── Radio ── */
    [data-testid="stRadio"] label {
        background: var(--s2) !important;
        border: 1px solid var(--b1) !important;
        border-radius: 10px !important;
        padding: 7px 16px !important;
        cursor: pointer !important;
        transition: all .15s !important;
    }
    [data-testid="stRadio"] label:has(input:checked) {
        border-color: rgba(243,156,18,.3) !important;
        background: var(--glow) !important;
    }
    [data-testid="stRadio"] label span { color: var(--t1) !important; font-size: 12px !important; }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        background: var(--s2) !important;
        border-radius: 10px !important;
        border: 1px solid var(--b1) !important;
        font-size: 12px !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: var(--s1) !important;
        border: 1px solid var(--b1) !important;
        border-radius: 14px !important;
        padding: 16px !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--t1) !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 28px !important;
        letter-spacing: .04em !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 9px !important; letter-spacing: .14em !important;
        text-transform: uppercase !important; color: var(--t3) !important;
    }

    /* ── Layout ── */
    .main .block-container { padding-top: 1.5rem !important; max-width: 1440px !important; }
    hr { border: none !important; height: 1px !important;
         background: linear-gradient(90deg,transparent,var(--b2),transparent) !important; }
    div[data-testid="stHtml"] { margin-bottom: -30px !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 3px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--b2); border-radius: 2px; }

    /* ── Date input ── */
    [data-testid="stDateInput"] > div {
        background: var(--s2) !important; border: 1px solid var(--b2) !important;
        border-radius: 10px !important;
    }

    @media (max-width: 768px) {
        iframe { height: 450px !important; }
        .main .block-container { padding-bottom: 1rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAP STYLES shared across all components
# ─────────────────────────────────────────────────────────────────────────────
_MAP_FONTS = '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Bebas+Neue&display=swap" rel="stylesheet"/>'

_HUD_CSS = """
.hud {
    position: absolute; z-index: 20;
    background: rgba(7,9,16,0.92);
    border: 1px solid rgba(243,156,18,0.22);
    border-radius: 14px; padding: 14px 18px;
    color: #F0F2F5; font-family: 'JetBrains Mono', monospace; font-size: 12px;
    line-height: 2.1; pointer-events: none;
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 8px 40px rgba(0,0,0,.7), inset 0 1px 0 rgba(255,255,255,.04);
}
.hud-title {
    font-size: 8px; letter-spacing: .2em; text-transform: uppercase;
    color: #4B5563; margin-bottom: 8px; padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,.05);
    font-family: 'JetBrains Mono', monospace;
}
.hud b { color: #F39C12; }
.tbadge {
    position: absolute; top: 60px; left: 14px; z-index: 20;
    background: rgba(7,9,16,0.92);
    border: 1px solid rgba(243,156,18,.25); border-radius: 10px;
    padding: 8px 16px; color: #F39C12; font-size: 14px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace; pointer-events: none;
    backdrop-filter: blur(12px); letter-spacing: .05em;
    box-shadow: 0 4px 20px rgba(243,156,18,.12);
}
.hint {
    position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
    z-index: 20; color: rgba(255,255,255,.25); font-size: 10px;
    pointer-events: none; font-family: 'JetBrains Mono', monospace;
    background: rgba(7,9,16,.65); padding: 5px 16px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,.04); white-space: nowrap; letter-spacing: .04em;
}
.tile-row {
    position: absolute; top: 14px; left: 14px; z-index: 20;
    display: flex; gap: 6px;
}
.tile-btn {
    background: rgba(7,9,16,.92); border: 1px solid rgba(255,255,255,.07);
    color: #6B7280; font-size: 11px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    padding: 6px 13px; border-radius: 9px; cursor: pointer;
    transition: all .2s; backdrop-filter: blur(8px); letter-spacing: .04em;
}
.tile-btn:hover { border-color: rgba(243,156,18,.3); color: #E8EAF0; }
.tile-btn.on { border-color: rgba(243,156,18,.35); color: #F39C12; background: rgba(243,156,18,.07); }
"""


# ─────────────────────────────────────────────────────────────────────────────
def render_map_component(lat, lon, radius_meters, path_data, animate_trigger,
                         sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el,
                         rise_edge, set_edge, rise_time, set_time, aqi_val):
    env    = st.session_state.env_data
    wind_js = ""
    if env.get("wind_dir") is not None and aqi_val != "Off":
        wd, wn = env["wind_dir"], env["wind_name"].upper()
        wind_js = f"""
        var wRad=(({wd}+180)*Math.PI/180);
        var sLat={lat}-((150/111111)*Math.cos(wRad));
        var sLon={lon}-((150/(111111*Math.cos({lat}*Math.PI/180)))*Math.sin(wRad));
        var eLat={lat}+((30/111111)*Math.cos(wRad));
        var eLon={lon}+((30/(111111*Math.cos({lat}*Math.PI/180)))*Math.sin(wRad));
        L.polyline([[sLat,sLon],[eLat,eLon]],{{color:'#3498db',weight:2.5,opacity:.7}}).addTo(map2);
        L.marker([eLat,eLon],{{icon:L.divIcon({{className:'',
            html:'<div style="transform:rotate({wd+180}deg);color:#3498db;font-size:16px;">▲</div>',
            iconSize:[16,16],iconAnchor:[8,8]}})}}).addTo(map2);"""

    html = f"""{_MAP_FONTS}
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
    {_HUD_CSS}
    body{{margin:0;background:#0A0C10;}}
    #map2{{height:560px;width:100%;border-radius:16px;
           border:1px solid rgba(243,156,18,.1);}}
    .sun-box{{background:linear-gradient(135deg,#F39C12,#E67E22);color:#000;
              padding:3px 9px;border-radius:7px;font-weight:700;font-size:11px;
              font-family:'JetBrains Mono',monospace;margin-bottom:2px;
              box-shadow:0 3px 10px rgba(243,156,18,.35);}}
    .sun-icon{{font-size:30pt;line-height:1;filter:drop-shadow(0 0 14px rgba(255,200,0,.85));}}
    .custom-sun-icon,.wind-arrow-container{{background:none;border:none;}}
    .leg-dot{{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle;}}
    </style>
    <div style="position:relative;">
      <div id="map2"></div>
      <div class="tile-row">
        <button class="tile-btn on" id="bs" onclick="setTile('s')">🗺 Street</button>
        <button class="tile-btn"    id="bsat" onclick="setTile('sat')">🛰 Satellite</button>
      </div>
      <div class="hud" style="top:14px;right:14px;min-width:190px;">
        <div class="hud-title">Solar Data</div>
        🌅 Sunrise &nbsp;<b>{rise_time}</b><br>
        🌇 Sunset &nbsp;&nbsp;<b>{set_time}</b><br>
        💨 AQI &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style="color:{'#F39C12' if aqi_val=='Off' else '#F39C12'};">{aqi_val}</b><br>
        <div style="margin-top:8px;font-size:9px;color:#4B5563;letter-spacing:.12em;text-transform:uppercase;">Legend</div>
        <div style="font-size:11px;"><span class="leg-dot" style="background:#E74C3C;"></span>Sunrise</div>
        <div style="font-size:11px;"><span class="leg-dot" style="background:#3498DB;"></span>Sunset</div>
        <div style="font-size:11px;"><span class="leg-dot" style="background:#555;"></span>Shadow</div>
      </div>
      <div class="hint">🖱 Drag · Scroll zoom</div>
    </div>
    <script>
    var TILES={{
      s:'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
      sat:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}'
    }};
    var curT='s', tL=null;
    var street=L.tileLayer(TILES.s), sat=L.tileLayer(TILES.sat);
    var map2=L.map('map2',{{center:[{lat},{lon}],zoom:17,layers:[street],zoomControl:false}});
    L.control.zoom({{position:'bottomright'}}).addTo(map2);
    tL=street;
    function setTile(m){{
      if(m===curT) return; curT=m;
      if(tL) map2.removeLayer(tL);
      tL=L.tileLayer(TILES[m]).addTo(map2);
      document.getElementById('bs').className='tile-btn'+(m==='s'?' on':'');
      document.getElementById('bsat').className='tile-btn'+(m==='sat'?' on':'');
    }}
    L.circle([{lat},{lon}],{{radius:{radius_meters},color:'rgba(243,156,18,.25)',
      weight:1.5,fillColor:'rgba(243,156,18,.04)',fillOpacity:1}}).addTo(map2);
    {wind_js}
    var pd={path_data};
    L.polyline(pd.map(p=>[p.lat,p.lon]),{{color:'#F39C12',weight:4,
      dashArray:'6,10',opacity:.75}}).addTo(map2);
    L.polyline([[{lat},{lon}],{rise_edge}],{{color:'#E74C3C',weight:2.5,opacity:.8}}).addTo(map2);
    L.polyline([[{lat},{lon}],{set_edge}], {{color:'#3498DB',weight:2.5,opacity:.8}}).addTo(map2);
    var sunIco=L.divIcon({{
      html:'<div style="text-align:center;line-height:1;"><div class="sun-icon" style="font-size:28pt;filter:drop-shadow(0 0 10px rgba(255,200,0,.9));">☀️</div><div class="sun-box" id="stl" style="margin-top:2px;">--:--</div></div>',
      iconSize:[60,60],iconAnchor:[30,22],className:'custom-sun-icon'
    }});
    var sunM=L.marker([0,0],{{icon:sunIco}}).addTo(map2);
    var shad=L.polyline([[{lat},{lon}],[{lat},{lon}]],{{color:'rgba(255,255,255,.2)',weight:3}}).addTo(map2);
    function upd(p){{
      if(!p) return;
      sunM.setLatLng([p.lat,p.lon]);
      shad.setLatLngs([[{lat},{lon}],[p.shlat,p.shlon]]);
      document.getElementById('stl').innerHTML=p.time;
      sunM.setOpacity(p.el<0?0:1);
      shad.setStyle({{opacity:p.el<0?0:.6}});
    }}
    if({str(animate_trigger).lower()}){{
      var i=0; setInterval(()=>{{upd(pd[i]);i=(i+1)%pd.length;}},150);
    }} else {{
      upd({{lat:{m_slat},lon:{m_slon},shlat:{m_shlat},shlon:{m_shlon},
            el:{m_el},time:"{sim_time.strftime('%H:%M')}"}});
    }}
    </script>"""
    components.html(html, height=580)


# ─────────────────────────────────────────────────────────────────────────────
def render_seasonal_map(lat, lon, radius, seasonal_paths):
    color_map = {"Summer":"#FF4444","Autumn":"#FF8C00","Spring":"#F1C40F","Winter":"#A8D8EA"}
    paths_js  = ""
    for sid, data in seasonal_paths.items():
        coords = data["coords"]
        if not coords: continue
        col = color_map.get(sid, "#fff")
        paths_js += f"""
        L.polyline({coords},{{color:'{col}',weight:5,opacity:.85}}).addTo(ms);
        L.circleMarker({coords[0]},{{radius:7,color:'rgba(255,255,255,.5)',weight:2,
          fillColor:'{col}',fillOpacity:1}}).addTo(ms)
         .bindTooltip('<b style="color:{col};font-family:JetBrains Mono,monospace;">{sid}</b>',
          {{permanent:true,direction:'top',className:'slbl'}});
        L.circleMarker({coords[-1]},{{radius:5,color:'rgba(255,255,255,.3)',weight:1,
          fillColor:'{col}',fillOpacity:.7}}).addTo(ms);"""

    sc = [lat, lon - 0.005]; rc = [lat, lon + 0.003]
    html = f"""{_MAP_FONTS}
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
    {_HUD_CSS}
    body{{margin:0;background:#0A0C10;}}
    #msmap{{height:620px;width:100%;border-radius:16px;border:1px solid rgba(243,156,18,.08);}}
    .slbl{{background:rgba(7,9,16,.88)!important;border:1px solid rgba(255,255,255,.1)!important;
           color:#fff!important;font-size:11px!important;padding:3px 8px!important;
           border-radius:6px!important;font-family:'JetBrains Mono',monospace!important;}}
    .leaflet-tooltip-top:before{{display:none!important;}}
    .loclbl{{background:transparent!important;border:none!important;box-shadow:none!important;
             font-family:'Bebas Neue',sans-serif!important;font-size:24px!important;
             letter-spacing:5px!important;pointer-events:none!important;}}
    .sr{{color:#FF4444!important;text-shadow:0 0 24px rgba(255,68,68,.5),2px 2px 6px #000!important;}}
    .ss{{color:#3498DB!important;text-shadow:0 0 24px rgba(52,152,219,.5),2px 2px 6px #000!important;}}
    </style>
    <div style="position:relative;">
      <div id="msmap"></div>
      <div class="hint">Seasonal sun path arcs · {lat:.4f}, {lon:.4f}</div>
    </div>
    <script>
    var sat=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
    var str=L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png');
    var ms=L.map('msmap',{{center:[{lat},{lon}],zoom:17,layers:[sat],zoomControl:false}});
    L.control.zoom({{position:'bottomright'}}).addTo(ms);
    L.control.layers({{"🛰 Satellite":sat,"🗺 Street":str}},null,{{position:'topleft',collapsed:false}}).addTo(ms);
    L.circle([{lat},{lon}],{{radius:{radius},color:'rgba(243,156,18,.15)',weight:1,fillOpacity:.02}}).addTo(ms);
    L.circleMarker([{lat},{lon}],{{radius:8,color:'#F39C12',weight:2,fillColor:'#F39C12',fillOpacity:.9}}).addTo(ms);
    L.marker({sc},{{opacity:0}}).addTo(ms).bindTooltip("SUNSET",{{permanent:true,direction:'center',className:'loclbl ss'}});
    L.marker({rc},{{opacity:0}}).addTo(ms).bindTooltip("SUNRISE",{{permanent:true,direction:'center',className:'loclbl sr'}});
    {paths_js}
    </script>"""
    components.html(html, height=630)


# ─────────────────────────────────────────────────────────────────────────────
def render_3d_shadow_component(lat, lon, radius_meters, path_data, animate_trigger,
                               sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el,
                               m_az, rise_time, set_time, allow_location_select=False):
    import json, math as _m

    all_pts  = json.dumps([{"lon":p["lon"],"lat":p["lat"],"shlat":p["shlat"],
                             "shlon":p["shlon"],"el":round(p["el"],2),
                             "az":round(p.get("az",0),2),"time":p["time"],
                             "iso":p.get("iso","")} for p in path_data])
    iso_list = json.dumps([p.get("iso", sim_time.isoformat()) for p in path_data])

    cur_time = sim_time.strftime("%H:%M")
    sim_iso  = sim_time.isoformat()
    sel_js      = "true" if allow_location_select else "false"
    hide_sun_js = "true" if allow_location_select else "false"
    hint_txt = ("Drag · Scroll zoom · ↔ rotate"
                if allow_location_select else
                "🖱 Drag · Scroll zoom · ↔ rotate · ▲▼ tilt")
    mel  = round(m_el, 2)
    maz  = round(m_az, 1)

    # Observer disc in 3D scene
    steps, rd = 20, 0.000035
    ring = []
    for i in range(steps+1):
        a = 2*_m.pi*i/steps
        ring.append([lon + rd*_m.cos(a)/_m.cos(_m.radians(lat)),
                     lat + rd*_m.sin(a)])
    obs_gj = json.dumps({
        "type":"FeatureCollection",
        "features":[{"type":"Feature",
                     "properties":{"color":"#F39C12","height":0.6,"minHeight":0},
                     "geometry":{"type":"Polygon","coordinates":[ring]}}]
    })

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
{_MAP_FONTS}
<link href="https://cdn.osmbuildings.org/4.1.1/OSMBuildings.css" rel="stylesheet"/>
<script src="https://cdn.osmbuildings.org/4.1.1/OSMBuildings.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:#0A0C10;overflow:hidden;}}
#map{{width:100%;height:600px;}}
{_HUD_CSS}
/* sun emoji */
#sun{{font-size:24px;line-height:1;pointer-events:none;position:absolute;
      transform:translate(-50%,-50%);display:none;
      filter:drop-shadow(0 0 12px rgba(255,200,0,.95));}}

/* coord */
#coord{{position:absolute;bottom:46px;left:50%;transform:translateX(-50%);
        z-index:29;background:rgba(7,9,16,.96);
        border:1px solid rgba(243,156,18,.3);border-radius:10px;
        padding:9px 22px;color:#F39C12;font-size:11px;font-weight:600;
        display:none;pointer-events:none;white-space:nowrap;
        font-family:'JetBrains Mono',monospace;letter-spacing:.05em;
        box-shadow:0 4px 24px rgba(243,156,18,.18);}}
/* ctrl buttons */
.cb{{background:rgba(7,9,16,.92);border:1px solid rgba(255,255,255,.07);
     color:#6B7280;font-size:13px;font-weight:700;padding:7px 12px;
     border-radius:9px;cursor:pointer;transition:all .15s;
     backdrop-filter:blur(8px);line-height:1;}}
.cb:hover{{border-color:rgba(243,156,18,.3);color:#E8EAF0;}}
.cb.N{{border-color:rgba(243,156,18,.25);color:#F39C12;font-size:10px;
       font-family:'JetBrains Mono',monospace;letter-spacing:.1em;}}
</style>
</head><body>
<div style="position:relative;width:100%;height:600px;">
  <div id="map"></div>

  <!-- tile toggle -->
  <div class="tile-row">
    <button class="tile-btn on" id="bs" onclick="setT('s')">🗺 Street</button>
    <button class="tile-btn"   id="bsat" onclick="setT('sat')">🛰 Satellite</button>
  </div>

  <!-- HUD -->
  <div class="hud" style="top:14px;right:14px;min-width:185px;">
    <div class="hud-title">Solar Position</div>
    🌅 Sunrise &nbsp;<b>{rise_time}</b><br>
    🌇 Sunset &nbsp;&nbsp;<b>{set_time}</b><br>
    ☀️ Elevation <b id="hel">{mel}°</b><br>
    🧭 Azimuth &nbsp;<b id="haz">{maz}°</b><br>
    🕐 Time &nbsp;&nbsp;&nbsp;&nbsp;<b id="htm">{cur_time}</b>
  </div>

  <!-- time badge -->
  <div class="tbadge">☀️ &nbsp;<span id="stm">{cur_time}</span></div>
  <div class="hint">{hint_txt}</div>

  <!-- rotate/tilt -->
  <div style="position:absolute;bottom:46px;right:14px;z-index:25;
    display:flex;flex-direction:column;gap:5px;align-items:center;">
    <button class="cb" onclick="aT(-10)">▲</button>
    <div style="display:flex;gap:5px;">
      <button class="cb" onclick="aR(-15)">◀</button>
      <button class="cb N" onclick="rst()">N</button>
      <button class="cb" onclick="aR(15)">▶</button>
    </div>
    <button class="cb" onclick="aT(10)">▼</button>
  </div>

  <!-- compass -->
  <div style="position:absolute;top:110px;right:14px;z-index:25;width:42px;height:42px;
    pointer-events:none;background:rgba(7,9,16,.88);border:1px solid rgba(255,255,255,.07);
    border-radius:50%;display:flex;align-items:center;justify-content:center;">
    <svg id="cmp" width="34" height="34" viewBox="-20 -20 40 40" style="transition:transform .2s;">
      <polygon points="0,-12 3,0 0,3 -3,0" fill="#E74C3C"/>
      <polygon points="0,12 3,0 0,-3 -3,0" fill="#374151"/>
      <text x="0" y="-14" text-anchor="middle" fill="#E74C3C"
            font-size="5.5" font-weight="bold" font-family="JetBrains Mono,monospace">N</text>
      <text x="0"   y="19" text-anchor="middle" fill="#374151" font-size="5.5" font-family="JetBrains Mono,monospace">S</text>
      <text x="15"  y="3"  text-anchor="middle" fill="#374151" font-size="5.5" font-family="JetBrains Mono,monospace">E</text>
      <text x="-15" y="3"  text-anchor="middle" fill="#374151" font-size="5.5" font-family="JetBrains Mono,monospace">W</text>
    </svg>
  </div>

  <div id="sun">☀️</div>
  <div id="coord">📍 &nbsp;<span id="ctxt"></span></div>
</div>

<script>
const D2R=Math.PI/180;
const HIDE_SUN={hide_sun_js};
const TILES={{s:'https://tile-a.openstreetmap.fr/hot/{{z}}/{{x}}/{{y}}.png',
              sat:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}'}};
let curT='s',tL=null;

const map=new OSMBuildings({{container:'map',
  position:{{latitude:{lat},longitude:{lon}}},
  zoom:17,minZoom:15,maxZoom:20,tilt:45,rotation:0,effects:['shadows'],
  attribution:'© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> · © <a href="https://osmbuildings.org/copyright">OSM Buildings</a>'
}});
map.setDate(new Date('{sim_iso}'));
tL=map.addMapTiles(TILES.s);
map.addGeoJSONTiles('https://{{s}}.data.osmbuildings.org/0.2/59fcc2e8/tile/{{z}}/{{x}}/{{y}}.json');
map.addGeoJSON({obs_gj},{{color:'#F39C12'}});

// Pre-drop a red pin at the currently selected location so it's
// visible as soon as the map loads — not just after clicking
(function(){{
  const rd=0.000022, steps=16;
  const ring=[];
  for(let i=0;i<=steps;i++){{
    const a=2*Math.PI*i/steps;
    const cosLat=Math.cos({lat}*Math.PI/180);
    ring.push([{lon}+rd*Math.cos(a)/cosLat, {lat}+rd*Math.sin(a)]);
  }}
  map.addGeoJSON({{
    type:"FeatureCollection",
    features:[
      {{type:"Feature",
        properties:{{color:"#F39C12",height:22,minHeight:0}},
        geometry:{{type:"Polygon",coordinates:[ring]}}}},
      {{type:"Feature",
        properties:{{color:"#ffffff",height:24,minHeight:20}},
        geometry:{{type:"Polygon",coordinates:[ring]}}}}
    ]
  }},{{color:'#F39C12'}});
}})();

function setT(m){{
  if(m===curT) return; curT=m;
  if(tL) map.remove(tL);
  tL=map.addMapTiles(TILES[m]);
  document.getElementById('bs').className='tile-btn'+(m==='s'?' on':'');
  document.getElementById('bsat').className='tile-btn'+(m==='sat'?' on':'');
}}

const allPts={all_pts}, isoList={iso_list};
allPts.forEach((p,i)=>p.iso=isoList[i]||'');

const sunEl=document.getElementById('sun');
const coord=document.getElementById('coord');
const ctxt=document.getElementById('ctxt');

let curRot=0,curTilt=45,curEl={mel},curAz={maz},pinGeo=null;
let pinLayer=null;  // GeoJSON pin rendered IN the 3D scene

// Build a pin GeoJSON disc — rendered IN the 3D scene, sticks to ground
function makePinGeoJSON(plat, plon) {{
  const rd=0.000022, steps=16;
  const ring=[];
  for(let i=0;i<=steps;i++){{
    const a=2*Math.PI*i/steps;
    const cosLat=Math.cos(plat*Math.PI/180);
    ring.push([plon+rd*Math.cos(a)/cosLat, plat+rd*Math.sin(a)]);
  }}
  return {{
    type:"FeatureCollection",
    features:[
      // Tall red spike so it's visible
      {{type:"Feature",
        properties:{{color:"#F39C12",height:22,minHeight:0}},
        geometry:{{type:"Polygon",coordinates:[ring]}}}},
      {{type:"Feature",
        properties:{{color:"#ffffff",height:24,minHeight:20}},
        geometry:{{type:"Polygon",coordinates:[ring]}}}}
    ]
  }};
}}
const anim={'true' if animate_trigger else 'false'};

function moveSun(az,el){{
  if(HIDE_SUN||el<-5){{sunEl.style.display='none';return;}}
  const W=document.getElementById('map').clientWidth||600;
  const H=document.getElementById('map').clientHeight||600;
  const f=Math.max(0,el)/90;
  // rx/ry shrink as sun rises toward zenith (centre of screen)
  const rx=W*.40*(1-f*.88), ry=H*.36*(1-f*.88);
  // az is clockwise from North. Subtract map rotation so it stays
  // geographically correct when user rotates the view.
  const ar=(az - curRot)*D2R;
  sunEl.style.display='block';
  // sin(ar) → east/west,  -cos(ar) → puts North at top (south at bottom)
  sunEl.style.left=(W/2 + rx*Math.sin(ar))+'px';
  sunEl.style.top =(H/2 - ry*Math.cos(ar)*0.55)+'px';
}}

function updateView(p){{
  if(p.iso) map.setDate(new Date(p.iso));
  curEl=p.el; curAz=p.az;
  moveSun(p.az,p.el);
  document.getElementById('hel').textContent=p.el.toFixed(1)+'°';
  document.getElementById('haz').textContent=p.az.toFixed(1)+'°';
  document.getElementById('htm').textContent=p.time;
  document.getElementById('stm').textContent=p.time;
}}

updateView({{lon:{m_slon},lat:{m_slat},shlat:{m_shlat},shlon:{m_shlon},
             el:{mel},az:{maz},time:'{cur_time}',iso:'{sim_iso}'}});

if(anim){{
  let i=0;
  setInterval(()=>{{updateView(allPts[i]);i=(i+1)%allPts.length;}},200);
}}

map.on('change',()=>{{moveSun(curAz,curEl);}});

function aR(d){{
  curRot=(curRot+d+360)%360;map.setRotation(curRot);
  document.getElementById('cmp').style.transform='rotate('+curRot+'deg)';
}}
function aT(d){{curTilt=Math.max(0,Math.min(70,curTilt+d));map.setTilt(curTilt);}}
function rst(){{
  curRot=0;curTilt=45;map.setRotation(0);map.setTilt(45);
  document.getElementById('cmp').style.transform='rotate(0deg)';
}}
map.on('rotate',()=>{{
  try{{curRot=((map.getRotation()%360)+360)%360;
    document.getElementById('cmp').style.transform='rotate('+curRot+'deg)';}}catch(e){{}}
}});

const SEL={sel_js};
let mdX=0,mdY=0;
if(SEL){{
  document.getElementById('map').addEventListener('mousedown',e=>{{mdX=e.clientX;mdY=e.clientY;}});
  map.on('pointerup',(t,d)=>{{
    if(Math.abs(d.x-mdX)>8||Math.abs(d.y-mdY)>8) return;
    const g=map.unproject(d.x,d.y);if(!g) return;
    pinGeo=g;drop(g.latitude,g.longitude);
    ctxt.textContent=g.latitude.toFixed(5)+', '+g.longitude.toFixed(5);
    coord.style.display='block';
    window.parent.postMessage({{type:'osm_pin',lat:g.latitude,lon:g.longitude}},'*');
  }});
  let tx=0,ty=0;
  document.getElementById('map').addEventListener('touchstart',e=>{{
    if(e.touches.length===1){{tx=e.touches[0].clientX;ty=e.touches[0].clientY;}}
  }},{{passive:true}});
  document.getElementById('map').addEventListener('touchend',e=>{{
    if(e.changedTouches.length!==1) return;
    const t=e.changedTouches[0];
    if(Math.abs(t.clientX-tx)>12||Math.abs(t.clientY-ty)>12) return;
    const r=document.getElementById('map').getBoundingClientRect();
    const g=map.unproject(t.clientX-r.left,t.clientY-r.top);if(!g) return;
    pinGeo=g;drop(g.latitude,g.longitude);
    ctxt.textContent=g.latitude.toFixed(5)+', '+g.longitude.toFixed(5);
    coord.style.display='block';
    window.parent.postMessage({{type:'osm_pin',lat:g.latitude,lon:g.longitude}},'*');
  }},{{passive:true}});
}}

// Drop pin as GeoJSON disc inside the 3D scene — sticks to ground like buildings
function drop(plat, plon){{
  if(pinLayer) map.remove(pinLayer);
  pinLayer = map.addGeoJSON(makePinGeoJSON(plat, plon), {{color:'#E74C3C'}});
}}
</script></body></html>"""
    components.html(html, height=660)


# ─────────────────────────────────────────────────────────────────────────────
def render_3d_map_component(lat, lon, radius_meters, path_data, animate_trigger,
                             sim_time, m_slat, m_slon, m_el, rise_time, set_time):
    cos_lat = math.cos(math.radians(lat))
    R = radius_meters
    pts = []
    for p in path_data:
        dx = (p["lon"] - lon) * 111111 * cos_lat
        dz = -(p["lat"] - lat) * 111111
        dy = max(0, p["el"]) * (R / 90.0) * 2.2
        pts.append({"x":round(dx,2),"y":round(dy,2),"z":round(dz,2),
                    "el":round(p["el"],2),"time":p["time"]})
    pts_js = str(pts).replace("'",'"').replace("True","true").replace("False","false")

    cx   = round((m_slon - lon) * 111111 * cos_lat, 2)
    cz   = round(-(m_slat - lat) * 111111, 2)
    cy   = round(max(0, m_el) * (R / 90.0) * 2.2, 2)
    ct   = sim_time.strftime('%H:%M')
    cd   = int(R * 2.2)
    ch   = int(R * 1.3)

    html = f"""<!DOCTYPE html><html><head>
{_MAP_FONTS}
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0A0C10;overflow:hidden;}}
canvas{{display:block;width:100%!important;height:600px!important;}}
{_HUD_CSS}
</style></head><body>
<canvas id="c"></canvas>
<div class="hud" style="top:14px;right:14px;min-width:160px;">
  <div class="hud-title">3D Arc View</div>
  🌅 Sunrise <b>{rise_time}</b><br>
  🌇 Sunset &nbsp;<b>{set_time}</b><br>
  ☀️ Elev &nbsp;&nbsp;&nbsp;<b id="hel">{m_el:.1f}°</b><br>
  🕐 Time &nbsp;&nbsp;&nbsp;<b id="htm">{ct}</b>
</div>
<div class="tbadge" style="top:14px;left:14px;">☀️ &nbsp;<span id="stm">{ct}</span></div>
<div class="hint">🖱 Drag to orbit · Scroll to zoom</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const cv=document.getElementById('c');
const W=cv.parentElement?cv.parentElement.clientWidth:window.innerWidth, H=600;
cv.width=W;cv.height=H;
const rend=new THREE.WebGLRenderer({{canvas:cv,antialias:true}});
rend.setPixelRatio(Math.min(devicePixelRatio,2));rend.setSize(W,H);rend.shadowMap.enabled=true;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x0A0C10);
scene.fog=new THREE.FogExp2(0x0A0C10,0.0007);
const cam=new THREE.PerspectiveCamera(50,W/H,0.5,8000);
cam.position.set({cd},{ch},{cd});cam.lookAt(0,0,0);
scene.add(new THREE.AmbientLight(0xffffff,0.35));
const dl=new THREE.DirectionalLight(0xffd580,1.8);
dl.position.set(300,600,300);dl.castShadow=true;scene.add(dl);
const R={R};
scene.add(new THREE.Mesh(new THREE.CylinderGeometry(R,R,3,80),
  new THREE.MeshLambertMaterial({{color:0x0D1118}})));
scene.add(new THREE.GridHelper(R*2,Math.max(10,Math.round(R/13)),0x151C28,0x0F1520));
scene.add(new THREE.Mesh(new THREE.TorusGeometry(R,2.5,8,80),
  new THREE.MeshBasicMaterial({{color:0x1A2535}})));
const lm=new THREE.LineBasicMaterial({{color:0x1A2535}});
[[[-R,0],[R,0]],[[0,-R],[0,R]]].forEach(([a,b])=>
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(
    [new THREE.Vector3(a[0],1,a[1]),new THREE.Vector3(b[0],1,b[1])]),lm)));
const pil=new THREE.Mesh(new THREE.CylinderGeometry(5.5,5.5,18,16),
  new THREE.MeshLambertMaterial({{color:0xF39C12}}));
pil.position.y=9;scene.add(pil);
scene.add(new THREE.Mesh(new THREE.TorusGeometry(11,2,8,32),
  new THREE.MeshBasicMaterial({{color:0xF39C12,transparent:true,opacity:.35}})));
function spr(txt,col){{
  const cv2=document.createElement('canvas');cv2.width=128;cv2.height=64;
  const c2=cv2.getContext('2d');
  c2.fillStyle=col;c2.font='bold 34px JetBrains Mono,monospace';
  c2.textAlign='center';c2.textBaseline='middle';c2.fillText(txt,64,32);
  const sp=new THREE.Sprite(new THREE.SpriteMaterial(
    {{map:new THREE.CanvasTexture(cv2),transparent:true,depthTest:false}}));
  sp.scale.set(48,24,1);return sp;
}}
const ld=R+52;
[['N','#E74C3C',0,-ld],['S','#2D3748',0,ld],['E','#2D3748',ld,0],['W','#2D3748',-ld,0]].forEach(([t,c,x,z])=>{{
  const s=spr(t,c);s.position.set(x,8,z);scene.add(s);
}});
const pd={pts_js};
const ap=pd.filter(p=>p.el>=0).map(p=>new THREE.Vector3(p.x,p.y,p.z));
if(ap.length>1){{
  const cv3=new THREE.CatmullRomCurve3(ap);
  scene.add(new THREE.Mesh(new THREE.TubeGeometry(cv3,ap.length*3,3,8,false),
    new THREE.MeshBasicMaterial({{color:0xF39C12,transparent:true,opacity:.82}})));
}}
pd.filter(p=>p.el>=0).forEach((p,i)=>{{
  if(i%4!==0) return;
  const col=new THREE.Color().setHSL(.09-(i/pd.length)*.04,1,.55);
  const d=new THREE.Mesh(new THREE.SphereGeometry(3.5,8,8),new THREE.MeshBasicMaterial({{color:col}}));
  d.position.set(p.x,p.y,p.z);scene.add(d);
}});
pd.filter(p=>p.el>=0).forEach((p,i)=>{{
  if(i%7!==0) return;
  const g=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(p.x,0,p.z),new THREE.Vector3(p.x,p.y,p.z)]);
  scene.add(new THREE.Line(g,new THREE.LineBasicMaterial({{color:0x2D1B00,transparent:true,opacity:.35}})));
}});
const sm=new THREE.Mesh(new THREE.SphereGeometry(14,24,24),new THREE.MeshBasicMaterial({{color:0xFFD700}}));
const hm=new THREE.Mesh(new THREE.SphereGeometry(22,24,24),new THREE.MeshBasicMaterial({{color:0xFF8800,transparent:true,opacity:.12,side:THREE.BackSide}}));
scene.add(sm);scene.add(hm);
const sg=[new THREE.Vector3(0,0,0),new THREE.Vector3(0,0,0)];
const sgeo=new THREE.BufferGeometry().setFromPoints(sg);
scene.add(new THREE.Line(sgeo,new THREE.LineBasicMaterial({{color:0x374151,transparent:true,opacity:.5}})));
function setSun(x,y,z,t,el){{
  sm.position.set(x,Math.max(0,y),z);hm.position.set(x,Math.max(0,y),z);
  const s=sgeo.attributes.position;
  s.setXYZ(0,0,.5,0);s.setXYZ(1,x===0?0:-x*2,.5,z===0?0:-z*2);s.needsUpdate=true;
  document.getElementById('hel').textContent=el.toFixed(1)+'°';
  document.getElementById('htm').textContent=t;
  document.getElementById('stm').textContent=t;
  sm.visible=el>=-2;hm.visible=el>=-2;
}}
setSun({cx},{cy},{cz},'{ct}',{m_el});
let ai=0;
if({'true' if animate_trigger else 'false'}){{
  setInterval(()=>{{const p=pd[ai];setSun(p.x,p.y,p.z,p.time,p.el);ai=(ai+1)%pd.length;}},160);
}}
let drag=false,prev={{x:0,y:0}},th=Math.PI/4,ph=Math.PI/3.5,cr={int(cd*1.3)};
function uCam(){{
  cam.position.set(cr*Math.sin(ph)*Math.sin(th),cr*Math.cos(ph),cr*Math.sin(ph)*Math.cos(th));
  cam.lookAt(0,0,0);
}}
uCam();
cv.addEventListener('mousedown',e=>{{drag=true;prev={{x:e.clientX,y:e.clientY}};}});
cv.addEventListener('mouseup',()=>drag=false);
cv.addEventListener('mousemove',e=>{{
  if(!drag) return;
  th-=(e.clientX-prev.x)*.005;
  ph=Math.max(.15,Math.min(Math.PI/2.1,ph+(e.clientY-prev.y)*.005));
  prev={{x:e.clientX,y:e.clientY}};uCam();
}});
cv.addEventListener('wheel',e=>{{cr=Math.max(R*.6,Math.min(R*4,cr+e.deltaY*.4));uCam();e.preventDefault();}},{{passive:false}});
let lt=null;
cv.addEventListener('touchstart',e=>lt=e.touches[0]);
cv.addEventListener('touchmove',e=>{{
  if(!lt) return;const t=e.touches[0];
  th-=(t.clientX-lt.clientX)*.005;
  ph=Math.max(.15,Math.min(Math.PI/2.1,ph+(t.clientY-lt.clientY)*.005));
  lt=t;uCam();e.preventDefault();
}},{{passive:false}});
(function loop(){{requestAnimationFrame(loop);rend.render(scene,cam);}})();
</script></body></html>"""
    components.html(html, height=620)
