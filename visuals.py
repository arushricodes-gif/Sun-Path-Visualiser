import streamlit as st
import streamlit.components.v1 as components
import math


def apply_styles(theme="dark"):
    """Minimal — just stores plot colors. All CSS is in app.py."""
    # Always light now
    st.session_state["_plot_bg"]   = "rgba(0,0,0,0)"
    st.session_state["_plot_grid"] = "rgba(0,0,0,0.06)"
    st.session_state["_plot_font"] = "#1A1A1A"
    st.components.v1.html("""
<script>
(function() {
  var css = `
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

    /* All inputs white */
    input, textarea,
    [data-baseweb="input"], [data-baseweb="base-input"],
    [data-baseweb="select"], [data-baseweb="select"] > div,
    [data-testid="stTextInput"] > div,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stDateInput"] > div > div {
      background-color: #ffffff !important;
      background: #ffffff !important;
      color: #1A1A1A !important;
      -webkit-text-fill-color: #1A1A1A !important;
    }
    input::placeholder { color: #999 !important; -webkit-text-fill-color: #999 !important; }
    [data-testid="stSelectbox"] span,
    [data-testid="stSelectbox"] div,
    [data-testid="stSelectbox"] p { color: #1A1A1A !important; -webkit-text-fill-color: #1A1A1A !important; }

    /* Dropdown portal */
    body [data-baseweb="popover"],
    body [data-baseweb="popover"] > div,
    body [data-baseweb="popover"] > div > div,
    body [data-baseweb="menu"],
    body [data-baseweb="menu"] > ul,
    body [data-baseweb="menu"] li,
    body [data-baseweb="list"],
    body li[role="option"],
    body div[role="option"],
    body [data-baseweb="option"],
    body [class*="menuList"],
    body [class*="option"],
    body [class*="menu"] > div {
      background-color: #ffffff !important;
      background: #ffffff !important;
      color: #1A1A1A !important;
      -webkit-text-fill-color: #1A1A1A !important;
    }
    body [data-baseweb="option"]:hover,
    body li[role="option"]:hover,
    body [data-baseweb="option"][aria-selected="true"],
    body li[role="option"][aria-selected="true"] {
      background-color: #FFF3E0 !important;
      color: #E07B00 !important;
      -webkit-text-fill-color: #E07B00 !important;
    }
    body [data-baseweb="option"] *,
    body [data-baseweb="menu"] span,
    body [data-baseweb="menu"] div,
    body li[role="option"] span,
    body li[role="option"] div { color: #1A1A1A !important; -webkit-text-fill-color: #1A1A1A !important; }

    [data-testid="stForm"] { background:#fff !important; border:2px solid #FFF3E0 !important; border-radius:16px !important; padding:16px !important; }

    [data-testid="stSlider"] p, [data-testid="stSlider"] span { color:#1A1A1A !important; -webkit-text-fill-color:#1A1A1A !important; }
    [data-testid="stThumbValue"] { color:#E07B00 !important; -webkit-text-fill-color:#E07B00 !important; font-weight:700 !important; }
    [data-testid="stToggle"] p, [data-testid="stToggle"] span { color:#1A1A1A !important; -webkit-text-fill-color:#1A1A1A !important; }
    [data-testid="stAlert"] p, [data-testid="stAlert"] span { color:#1A1A1A !important; -webkit-text-fill-color:#1A1A1A !important; }

    .js-plotly-plot .plotly .bg { fill:transparent !important; }
    .leaflet-control-attribution, .osmb-attribution { display:none !important; }

    body [data-baseweb="calendar"],
    body [data-baseweb="datepicker"],
    body [class*="react-datepicker"],
    body div[role="dialog"],
    body table[role="grid"],
    body table[role="grid"] td,
    body table[role="grid"] th,
    body table[role="grid"] tr,
    body [aria-label*="calendar"],
    body [class*="CalendarMonth"],
    body [class*="DayPicker"],
    body [class*="datepicker"],
    body [data-testid="stDateInput"] + div,
    body [data-baseweb="calendar"] *:not([aria-selected="true"]):not([data-selected="true"]) {
      background-color: #ffffff !important;
      background: #ffffff !important;
      color: #1A1A1A !important;
      -webkit-text-fill-color: #1A1A1A !important;
    }
    body [data-baseweb="calendar"] button,
    body [data-baseweb="datepicker"] button {
      background: transparent !important;
      color: #E07B00 !important;
      -webkit-text-fill-color: #E07B00 !important;
    }
    body [data-baseweb="calendar"] select,
    body [data-baseweb="calendar"] [data-baseweb="select"] > div {
      background: #fff !important;
      color: #1A1A1A !important;
    }
  `;
  function inject(doc) {
    var s = doc.createElement('style');
    s.id = 'sunscout-global';
    s.textContent = css;
    (doc.head || doc.documentElement).appendChild(s);
  }
  try { inject(window.parent.document); } catch(e) { inject(document); }

  function forceWhite(n) {
    if (!n || n.nodeType !== 1) return;
    n.style.setProperty('background-color','#ffffff','important');
    n.style.setProperty('color','#1A1A1A','important');
    n.style.setProperty('-webkit-text-fill-color','#1A1A1A','important');
    var all = n.querySelectorAll ? n.querySelectorAll('*') : [];
    for (var i=0; i<all.length; i++) {
      var el = all[i];
      if (el.getAttribute && el.getAttribute('aria-selected') === 'true') continue;
      el.style.setProperty('background-color','#ffffff','important');
      el.style.setProperty('color','#1A1A1A','important');
      el.style.setProperty('-webkit-text-fill-color','#1A1A1A','important');
    }
  }

  function isPortal(n) {
    if (!n || !n.getAttribute) return false;
    var bw = n.getAttribute('data-baseweb');
    if (bw === 'popover' || bw === 'menu' || bw === 'datepicker') return true;
    if (n.querySelector && (
      n.querySelector('[data-baseweb="menu"]') ||
      n.querySelector('[data-baseweb="calendar"]') ||
      n.querySelector('table[role="grid"]') ||
      n.querySelector('[aria-label*="calendar"]') ||
      n.querySelector('[class*="CalendarDay"]') ||
      n.querySelector('[class*="calendar"]')
    )) return true;
    return false;
  }

  function watchPortals(doc) {
    var obs = new MutationObserver(function(mutations) {
      mutations.forEach(function(m) {
        m.addedNodes.forEach(function(n) {
          if (n.nodeType === 1 && isPortal(n)) {
            forceWhite(n);
            var inner = new MutationObserver(function() { forceWhite(n); });
            inner.observe(n, { childList: true, subtree: true, attributes: true });
          }
        });
      });
    });
    obs.observe(doc.body, { childList: true, subtree: false });
  }
  try { watchPortals(window.parent.document); } catch(e) {}
})();
</script>
""", height=0)


_MAP_FONTS = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet"/>'

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
.leaflet-control-attribution,
.leaflet-control-attribution a,
.osmb-attribution { display: none !important; }
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
                         sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
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
           border:1px solid rgba(243,156,18,.1);cursor:crosshair;}}
    .sun-box{{background:linear-gradient(135deg,#F39C12,#E67E22);color:#000;
              padding:3px 9px;border-radius:7px;font-weight:700;font-size:11px;
              font-family:'JetBrains Mono',monospace;margin-bottom:2px;
              box-shadow:0 3px 10px rgba(243,156,18,.35);}}
    .sun-icon{{font-size:30pt;line-height:1;filter:drop-shadow(0 0 14px rgba(255,200,0,.85));}}
    .custom-sun-icon,.wind-arrow-container{{background:none;border:none;}}
    .leg-dot{{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle;}}
    #click-hint{{
        position:absolute;bottom:46px;left:50%;transform:translateX(-50%);
        z-index:25;background:rgba(7,9,16,.88);border:1px solid rgba(243,156,18,.3);
        border-radius:10px;padding:7px 18px;color:#F39C12;font-size:11px;font-weight:600;
        font-family:'JetBrains Mono',monospace;pointer-events:none;white-space:nowrap;
        letter-spacing:.05em;opacity:0;transition:opacity .4s;
    }}
    #hud2d * {{ color: inherit !important; -webkit-text-fill-color: inherit !important; }}
    #hud2d .hud-label {{ color: #9CA3AF !important; -webkit-text-fill-color: #9CA3AF !important; }}
    #hud2d .hud-val-orange {{ color: #F39C12 !important; -webkit-text-fill-color: #F39C12 !important; }}
    #hud2d .hud-val-white {{ color: #F0F2F5 !important; -webkit-text-fill-color: #F0F2F5 !important; }}
    #hud2d .leg-red {{ color: #E74C3C !important; -webkit-text-fill-color: #E74C3C !important; }}
    #hud2d .leg-blue {{ color: #3498DB !important; -webkit-text-fill-color: #3498DB !important; }}
    #hud2d .leg-grey {{ color: #8B9AB0 !important; -webkit-text-fill-color: #8B9AB0 !important; }}
    </style>
    <div style="position:relative;height:560px;">
      <div id="map2" style="height:560px;width:100%;"></div>
      <div class="tile-row">
        <button class="tile-btn on" id="bs" onclick="setTile('s')">Street</button>
        <button class="tile-btn"    id="bsat" onclick="setTile('sat')">Satellite</button>
      </div>
      <div style="position:absolute;bottom:48px;left:14px;z-index:9999;
        background:rgba(255,255,255,0.97);border:2px solid rgba(224,123,0,0.2);
        border-radius:14px;padding:12px 16px;pointer-events:none;
        box-shadow:0 4px 16px rgba(0,0,0,0.1);font-family:sans-serif;">
        <div style="font-size:10px;font-weight:800;color:#888;text-transform:uppercase;
             letter-spacing:.1em;margin-bottom:8px;">Legend</div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
          <span style="display:inline-block;width:28px;height:4px;background:#E74C3C;border-radius:2px;flex-shrink:0;"></span>
          <span style="font-size:12px;font-weight:700;color:#E74C3C;">Sunrise dir</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
          <span style="display:inline-block;width:28px;height:4px;background:#3498DB;border-radius:2px;flex-shrink:0;"></span>
          <span style="font-size:12px;font-weight:700;color:#3498DB;">Sunset dir</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
          <span style="display:inline-block;width:28px;height:0;border-top:3px dashed #8B9AB0;flex-shrink:0;"></span>
          <span style="font-size:12px;font-weight:700;color:#8B9AB0;">Shadow</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="display:inline-block;width:28px;height:0;border-top:3px dashed #E07B00;flex-shrink:0;"></span>
          <span style="font-size:12px;font-weight:700;color:#E07B00;">Sun path</span>
        </div>
      </div>
      <div class="hint">🖱 Click to move pin · Drag · Scroll zoom</div>
      <div id="click-hint">📍 Pin moved!</div>
    </div>
    <script>
    var TILES={{
      s:'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
      sat:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}'
    }};
    var curT='s', tL=null;
    var street=L.tileLayer(TILES.s), sat=L.tileLayer(TILES.sat);
    var map2=L.map('map2',{{center:[{lat},{lon}],zoom:17,layers:[street],zoomControl:false,attributionControl:false}});
    L.control.zoom({{position:'bottomright'}}).addTo(map2);
    tL=street;
    function setTile(m){{
      if(m===curT) return; curT=m;
      if(tL) map2.removeLayer(tL);
      tL=L.tileLayer(TILES[m]).addTo(map2);
      document.getElementById('bs').className='tile-btn'+(m==='s'?' on':'');
      document.getElementById('bsat').className='tile-btn'+(m==='sat'?' on':'');
    }}

    var pinMarker = L.marker([{lat},{lon}], {{
        icon: L.divIcon({{
            html: '<div style="font-size:22px;filter:drop-shadow(0 0 6px rgba(243,156,18,.8));">📍</div>',
            iconSize:[28,28], iconAnchor:[14,28], className:''
        }})
    }}).addTo(map2);

    var clickHint = document.getElementById('click-hint');
    var hintTimer = null;

    map2.on('click', function(e) {{
        var newLat = e.latlng.lat;
        var newLon = e.latlng.lng;
        pinMarker.setLatLng([newLat, newLon]);
        clickHint.style.opacity = '1';
        clearTimeout(hintTimer);
        hintTimer = setTimeout(function(){{ clickHint.style.opacity='0'; }}, 1500);
        try {{
            window.parent.sessionStorage.setItem('map2d_click',
                JSON.stringify({{lat: newLat, lon: newLon}}));
        }} catch(err) {{}}
    }});

    L.circle([{lat},{lon}],{{radius:{radius_meters},color:'rgba(243,156,18,.25)',
      weight:1.5,fillColor:'rgba(243,156,18,.04)',fillOpacity:1}}).addTo(map2);
    {wind_js}
    var pd={path_data};
    L.polyline(pd.map(p=>[p.lat,p.lon]),{{color:'#F39C12',weight:7,
      dashArray:'8,12',opacity:.85}}).addTo(map2);
    L.polyline([[{lat},{lon}],{rise_edge}],{{color:'#E74C3C',weight:5,opacity:.85}}).addTo(map2);
    L.polyline([[{lat},{lon}],{set_edge}], {{color:'#3498DB',weight:5,opacity:.85}}).addTo(map2);
    var sunIco=L.divIcon({{
      html:'<div style="text-align:center;line-height:1;"><div class="sun-icon" style="font-size:28pt;filter:drop-shadow(0 0 10px rgba(255,200,0,.9));">☀️</div><div class="sun-box" id="stl" style="margin-top:2px;">--:--</div></div>',
      iconSize:[60,60],iconAnchor:[30,22],className:'custom-sun-icon'
    }});
    var sunM=L.marker([0,0],{{icon:sunIco}}).addTo(map2);
    var shad=L.polyline([[{lat},{lon}],[{lat},{lon}]],{{color:'#8B9AB0',weight:5,dashArray:'6,10',opacity:.80}}).addTo(map2);
    function upd(p){{
      if(!p) return;
      sunM.setLatLng([p.lat,p.lon]);
      shad.setLatLngs([[{lat},{lon}],[p.shlat,p.shlon]]);
      document.getElementById('stl').innerHTML=p.time;
      sunM.setOpacity(p.el<0?0:1);
      shad.setStyle({{opacity:p.el<0?0:.7}});
      var elEl=document.getElementById('hud2d-el');
      var azEl=document.getElementById('hud2d-az');
      var tmEl=document.getElementById('hud2d-tm');
      if(elEl) elEl.textContent=(p.el!=null?p.el.toFixed(1)+'°':'--°');
      if(azEl) azEl.textContent=(p.az!=null?p.az.toFixed(1)+'°':'--°');
      if(tmEl) tmEl.textContent=p.time;
    }}
    (function(){{
      var elEl=document.getElementById('hud2d-el');
      var azEl=document.getElementById('hud2d-az');
      var tmEl=document.getElementById('hud2d-tm');
      if(elEl) elEl.textContent='{m_el:.1f}°';
      if(azEl) azEl.textContent='{m_az:.1f}°';
      if(tmEl) tmEl.textContent='{sim_time.strftime('%H:%M')}';
    }})();
    if({str(animate_trigger).lower()}){{
      var i=0; setInterval(()=>{{upd(pd[i]);i=(i+1)%pd.length;}},150);
    }} else {{
      upd({{lat:{m_slat},lon:{m_slon},shlat:{m_shlat},shlon:{m_shlon},
            el:{m_el},az:{m_az},time:"{sim_time.strftime('%H:%M')}"}});
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
    var ms=L.map('msmap',{{center:[{lat},{lon}],zoom:17,layers:[str],zoomControl:false,attributionControl:false}});
    L.control.zoom({{position:'bottomright'}}).addTo(ms);
    L.control.layers({{"🛰 Satellite":sat,"🗺 Street":str}},null,{{position:'topleft',collapsed:false}}).addTo(ms);
    L.circle([{lat},{lon}],{{radius:{radius},color:'rgba(243,156,18,.55)',weight:2,fillColor:'rgba(243,156,18,.06)',fillOpacity:1,dashArray:'6,6'}}).addTo(ms);
    L.circleMarker([{lat},{lon}],{{radius:8,color:'#F39C12',weight:2,fillColor:'#F39C12',fillOpacity:.9}}).addTo(ms);
    L.marker({sc},{{opacity:0}}).addTo(ms).bindTooltip("SUNSET",{{permanent:true,direction:'center',className:'loclbl ss'}});
    L.marker({rc},{{opacity:0}}).addTo(ms).bindTooltip("SUNRISE",{{permanent:true,direction:'center',className:'loclbl sr'}});
    {paths_js}
    </script>"""
    components.html(html, height=630)


# ─────────────────────────────────────────────────────────────────────────────
def render_3d_shadow_component(lat, lon, radius_meters, path_data, animate_trigger,
                               sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el,
                               m_az, rise_time, set_time, allow_location_select=False,
                               init_rot=0, init_tilt=0, init_zoom=1.3):
    import json, math as _m

    all_pts = json.dumps([{
        "lon":  p["lon"],  "lat":  p["lat"],
        "shlat":p["shlat"],"shlon":p["shlon"],
        "el":   round(p["el"], 2),
        "az":   round(p.get("az", 0), 2),
        "time": p["time"],
        "iso":  p.get("iso", "")
    } for p in path_data])
    iso_list = json.dumps([p.get("iso", sim_time.isoformat()) for p in path_data])

    sun_path_coords = json.dumps([
        [p["lon"], p["lat"]]
        for p in path_data if p["el"] >= 0
    ])

    cur_time = sim_time.strftime("%H:%M")
    cur_date = sim_time.strftime("%b %d, %Y")
    sim_iso  = sim_time.isoformat()

    sel_js      = "true" if allow_location_select else "false"
    hide_sun_js = "true" if allow_location_select else "false"
    hint_txt    = ("Drag · Scroll zoom · ↔ rotate"
                   if allow_location_select else
                   "🖱 Drag · Scroll zoom · ↔ rotate · ▲▼ tilt")
    mel = round(m_el, 2)
    maz = round(m_az, 1)

    steps, rd = 20, 0.000035
    ring = []
    for i in range(steps + 1):
        a = 2 * _m.pi * i / steps
        ring.append([lon + rd * _m.cos(a) / _m.cos(_m.radians(lat)),
                     lat + rd * _m.sin(a)])
    obs_gj = json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature",
                      "properties": {"color": "#F39C12", "height": 0.6, "minHeight": 0},
                      "geometry": {"type": "Polygon", "coordinates": [ring]}}]
    })

    sun_path_gj = json.dumps({
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"color": "#F39C12", "height": 1.5, "minHeight": 0},
            "geometry": {"type": "LineString", "coordinates": json.loads(sun_path_coords)}
        }]
    })

    # Pin ring — height set dynamically in JS based on nearby buildings
    pin_ring_js = json.dumps(ring)

    init_rot  = float(init_rot)  % 360
    init_tilt = max(0.0, min(70.0, float(init_tilt)))

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
{_MAP_FONTS}
<link href="https://cdn.osmbuildings.org/4.1.1/OSMBuildings.css" rel="stylesheet"/>
<script src="https://cdn.osmbuildings.org/4.1.1/OSMBuildings.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:#0A0C10;overflow:hidden;}}
#map{{width:100%;height:600px;}}
{_HUD_CSS}
#sun{{font-size:36px;line-height:1;pointer-events:none;position:absolute;
      transform:translate(-50%,-50%);display:none;
      filter:drop-shadow(0 0 18px rgba(255,200,0,.95));}}
#arc-svg{{position:absolute;top:0;left:0;width:100%;height:100%;
          pointer-events:none;z-index:18;overflow:visible;}}
#coord{{position:absolute;bottom:46px;left:50%;transform:translateX(-50%);
        z-index:29;background:rgba(7,9,16,.96);
        border:1px solid rgba(243,156,18,.3);border-radius:10px;
        padding:9px 22px;color:#F39C12;font-size:11px;font-weight:600;
        display:none;pointer-events:none;white-space:nowrap;
        font-family:'JetBrains Mono',monospace;letter-spacing:.05em;
        box-shadow:0 4px 24px rgba(243,156,18,.18);}}
.cb{{background:#fff;border:2px solid #E5E7EB;
     color:#555;font-size:14px;font-weight:700;padding:8px 12px;
     border-radius:10px;cursor:pointer;transition:all .15s;line-height:1;}}
.cb:hover{{border-color:#E07B00;color:#E07B00;background:#FFF3E0;}}
.cb.N{{border-color:rgba(224,123,0,.4);color:#E07B00;font-size:11px;
       font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;letter-spacing:.06em;}}

</style>
</head><body>
<div style="position:relative;width:100%;height:600px;">
  <div id="map"></div>

  <div class="tile-row">
    <button class="tile-btn on" id="bs" onclick="setT('s')">🗺 Street</button>
    <button class="tile-btn"   id="bsat" onclick="setT('sat')">🛰 Satellite</button>
  </div>

  <div class="tbadge">☀️ &nbsp;<span id="stm">{cur_time}</span></div>
  <div class="hint">{hint_txt}</div>

  <!-- Viewing angle controls — top right -->
  <div style="position:absolute;top:14px;right:14px;z-index:25;
    display:flex;flex-direction:column;gap:6px;align-items:center;
    background:rgba(255,255,255,0.95);border:2px solid rgba(224,123,0,0.25);
    border-radius:16px;padding:12px 10px;
    box-shadow:0 4px 20px rgba(0,0,0,0.12);">
    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:10px;font-weight:800;
         color:#E07B00;text-transform:uppercase;letter-spacing:.08em;margin-bottom:2px;
         white-space:nowrap;">Set viewing angle</div>
    <button class="cb" onclick="aT(-10)">▲</button>
    <div style="display:flex;gap:5px;">
      <button class="cb" onclick="aR(-15)">◀</button>
      <button class="cb N" onclick="rst()">N</button>
      <button class="cb" onclick="aR(15)">▶</button>
    </div>
    <button class="cb" onclick="aT(10)">▼</button>
  </div>

  <!-- Compass — below the controls box -->
  <div style="position:absolute;top:198px;right:22px;z-index:25;width:42px;height:42px;
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

  <svg id="arc-svg"></svg>
  <div id="sun">☀️</div>
  <!-- Pin dot: always visible at map center -->
  <div id="pin-wrap" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
       pointer-events:none;z-index:22;">
    <div id="pin-dot" style="width:14px;height:14px;border-radius:50%;
         background:#E07B00;border:3px solid #fff;
         box-shadow:0 0 0 3px rgba(224,123,0,0.45);"></div>
  </div>
  <div id="coord">📍 &nbsp;<span id="ctxt"></span></div>
</div>

<script>
const D2R = Math.PI/180;
const HIDE_SUN = {hide_sun_js};
const TILES = {{
  s:   'https://tile-a.openstreetmap.fr/hot/{{z}}/{{x}}/{{y}}.png',
  sat: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}'
}};
let curT = 's', tL = null;

let curRot  = {init_rot:.1f};
let curTilt = {init_tilt:.1f};

const map = new OSMBuildings({{
  container: 'map',
  position:  {{latitude: {lat}, longitude: {lon}}},
  zoom: 17, minZoom: 15, maxZoom: 20,
  tilt:     curTilt,
  rotation: curRot,
  effects:  ['shadows'],
  attribution: ''
}});
map.setDate(new Date('{sim_iso}'));
tL = map.addMapTiles(TILES.s);
map.addGeoJSONTiles('https://{{s}}.data.osmbuildings.org/0.2/59fcc2e8/tile/{{z}}/{{x}}/{{y}}.json');




function setT(m) {{
  if(m===curT) return; curT=m;
  if(tL) map.remove(tL);
  tL=map.addMapTiles(TILES[m]);
  document.getElementById('bs').className  = 'tile-btn'+(m==='s'  ?' on':'');
  document.getElementById('bsat').className= 'tile-btn'+(m==='sat'?' on':'');
}}

// ── Fetch building height async, just for reference ──────────────────────────
(function() {{
  const q = '[out:json][timeout:10];(way["building"](around:60,{lat},{lon});relation["building"](around:60,{lat},{lon}););out center tags;';
  fetch('https://overpass-api.de/api/interpreter', {{
    method: 'POST', body: 'data=' + encodeURIComponent(q)
  }})
  .then(r => r.json())
  .catch(() => {{}});
}})();

const allPts  = {all_pts};
const isoList = {iso_list};
allPts.forEach((p,i) => p.iso = isoList[i] || '');

const sunEl = document.getElementById('sun');
const coord = document.getElementById('coord');
const ctxt  = document.getElementById('ctxt');
let curEl = {mel}, curAz = {maz};

function saveCam() {{
  try {{
    const url = new URL(window.parent.location.href);
    url.searchParams.set('cam_rot',  curRot.toFixed(1));
    url.searchParams.set('cam_tilt', curTilt.toFixed(1));
    window.parent.history.replaceState({{}}, '', url.toString());
  }} catch(e) {{}}
}}

function aR(d) {{
  curRot = (curRot + d + 360) % 360;
  map.setRotation(curRot);
  document.getElementById('cmp').style.transform = 'rotate('+curRot+'deg)';
  if(!HIDE_SUN) drawArc();
  saveCam();
}}
function aT(d) {{
  curTilt = Math.max(0, Math.min(70, curTilt + d));
  map.setTilt(curTilt);
  if(!HIDE_SUN) drawArc();
  saveCam();
}}
function rst() {{
  curRot=0; curTilt=45;
  map.setRotation(0); map.setTilt(45);
  document.getElementById('cmp').style.transform = 'rotate(0deg)';
  if(!HIDE_SUN) drawArc();
  saveCam();
}}

map.on('rotate', () => {{
  try {{
    curRot = ((map.getRotation()%360)+360)%360;
    document.getElementById('cmp').style.transform = 'rotate('+curRot+'deg)';
    if(!HIDE_SUN) drawArc();
    saveCam();
  }} catch(e) {{}}
}});

const arcSvg = document.getElementById('arc-svg');

function projectToScreen(az, el) {{
  const W = document.getElementById('map').clientWidth  || 800;
  const H = document.getElementById('map').clientHeight || 600;
  const f  = Math.max(0, el) / 90;
  const rx = W * 0.48 * (1 - f);
  const ry = H * 0.44 * (1 - f);
  const ar = (az - curRot) * D2R;
  return [W/2 + rx*Math.sin(ar), H/2 - ry*Math.cos(ar)*0.6];
}}

function drawArc() {{
  const W = document.getElementById('map').clientWidth  || 800;
  const H = document.getElementById('map').clientHeight || 600;
  arcSvg.setAttribute('viewBox', '0 0 '+W+' '+H);
  while (arcSvg.firstChild) arcSvg.removeChild(arcSvg.firstChild);
  const abovePts = allPts.filter(p => p.el >= 0);
  if (abovePts.length < 2) return;
  const screenPts = abovePts.map(p => projectToScreen(p.az, p.el));
  const glow = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  glow.setAttribute('points', screenPts.map(p => p[0].toFixed(1)+','+p[1].toFixed(1)).join(' '));
  glow.setAttribute('fill', 'none');
  glow.setAttribute('stroke', 'rgba(255,180,0,0.18)');
  glow.setAttribute('stroke-width', '14');
  glow.setAttribute('stroke-linecap', 'round');
  glow.setAttribute('stroke-linejoin', 'round');
  arcSvg.appendChild(glow);
  const glow2 = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  glow2.setAttribute('points', screenPts.map(p => p[0].toFixed(1)+','+p[1].toFixed(1)).join(' '));
  glow2.setAttribute('fill', 'none');
  glow2.setAttribute('stroke', 'rgba(255,200,80,0.28)');
  glow2.setAttribute('stroke-width', '6');
  glow2.setAttribute('stroke-linecap', 'round');
  glow2.setAttribute('stroke-linejoin', 'round');
  arcSvg.appendChild(glow2);
  const arc = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  arc.setAttribute('points', screenPts.map(p => p[0].toFixed(1)+','+p[1].toFixed(1)).join(' '));
  arc.setAttribute('fill', 'none');
  arc.setAttribute('stroke', '#F39C12');
  arc.setAttribute('stroke-width', '2.5');
  arc.setAttribute('stroke-linecap', 'round');
  arc.setAttribute('stroke-linejoin', 'round');
  arc.setAttribute('stroke-dasharray', '6 9');
  arc.setAttribute('opacity', '0.92');
  arcSvg.appendChild(arc);
  abovePts.forEach((p, i) => {{
    if (i % 3 !== 0) return;
    const [sx, sy] = projectToScreen(p.az, p.el);
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('cx', sx.toFixed(1));
    dot.setAttribute('cy', sy.toFixed(1));
    dot.setAttribute('r', '2.8');
    dot.setAttribute('fill', '#FFD06D');
    dot.setAttribute('opacity', '0.85');
    arcSvg.appendChild(dot);
  }});
  const labels = [
    {{ pt: screenPts[0],                 txt: '🌅 Rise', anchor: 'end'   }},
    {{ pt: screenPts[screenPts.length-1], txt: 'Set 🌇',  anchor: 'start' }},
  ];
  labels.forEach(lbl => {{
    const [lx, ly] = lbl.pt;
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', lx.toFixed(1));
    circle.setAttribute('cy', ly.toFixed(1));
    circle.setAttribute('r', '4.5');
    circle.setAttribute('fill', '#F39C12');
    circle.setAttribute('opacity', '0.95');
    arcSvg.appendChild(circle);
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttribute('x', (lx + (lbl.anchor === 'end' ? -10 : 10)).toFixed(1));
    t.setAttribute('y', (ly - 8).toFixed(1));
    t.setAttribute('fill', '#FFD06D');
    t.setAttribute('font-size', '10');
    t.setAttribute('font-family', 'JetBrains Mono, monospace');
    t.setAttribute('font-weight', '600');
    t.setAttribute('text-anchor', lbl.anchor);
    t.setAttribute('opacity', '0.9');
    t.textContent = lbl.txt;
    arcSvg.appendChild(t);
  }});
}}

if(!HIDE_SUN) drawArc();

function moveSun(az, el) {{
  if(HIDE_SUN || el < -5) {{ sunEl.style.display='none'; return; }}
  const [sx, sy] = projectToScreen(az, el);
  sunEl.style.display = 'block';
  sunEl.style.left = sx + 'px';
  sunEl.style.top  = sy + 'px';
}}

function updateView(p) {{
  if(p.iso) map.setDate(new Date(p.iso));
  curEl = p.el; curAz = p.az;
  moveSun(p.az, p.el);
  var stm=document.getElementById('stm'); if(stm) stm.textContent=p.time;
}}

updateView({{
  lon:{m_slon}, lat:{m_slat}, shlat:{m_shlat}, shlon:{m_shlon},
  el:{mel}, az:{maz}, time:'{cur_time}', iso:'{sim_iso}'
}});

const anim = {'true' if animate_trigger else 'false'};
if(anim) {{
  let i=0;
  setInterval(() => {{ updateView(allPts[i]); i=(i+1)%allPts.length; }}, 200);
}}

map.on('change', () => {{ moveSun(curAz, curEl); if(!HIDE_SUN) drawArc(); }});

function makePinGeoJSON(plat, plon, pinH) {{
  pinH = pinH || 60;
  const capH = pinH + 3;
  const rd=0.000022, steps=16, ring=[];
  for(let i=0;i<=steps;i++){{
    const a=2*Math.PI*i/steps;
    const cosLat=Math.cos(plat*Math.PI/180);
    ring.push([plon+rd*Math.cos(a)/cosLat, plat+rd*Math.sin(a)]);
  }}
  return {{
    type:"FeatureCollection",
    features:[
      {{type:"Feature",properties:{{color:"#F39C12",height:pinH,minHeight:0}},
        geometry:{{type:"Polygon",coordinates:[ring]}}}},
      {{type:"Feature",properties:{{color:"#E07B00",height:capH,minHeight:pinH}},
        geometry:{{type:"Polygon",coordinates:[ring]}}}}
    ]
  }};
}}

function drop(plat, plon) {{
  if(pinLayer) map.remove(pinLayer);
  pinLayer = map.addGeoJSON(makePinGeoJSON(plat, plon, 60), {{color:'#F39C12'}});
}}

const SEL = {sel_js};
let mdX=0, mdY=0;
if(SEL) {{
  document.getElementById('map').addEventListener('mousedown', e => {{ mdX=e.clientX; mdY=e.clientY; }});
  map.on('pointerup', (t, d) => {{
    if(Math.abs(d.x-mdX)>8 || Math.abs(d.y-mdY)>8) return;
    const g = map.unproject(d.x, d.y); if(!g) return;
    drop(g.latitude, g.longitude);
    ctxt.textContent = g.latitude.toFixed(5)+', '+g.longitude.toFixed(5);
    coord.style.display = 'block';
    window.parent.postMessage({{type:'osm_pin', lat:g.latitude, lon:g.longitude}}, '*');
  }});
  let tx=0, ty=0;
  document.getElementById('map').addEventListener('touchstart', e => {{
    if(e.touches.length===1){{ tx=e.touches[0].clientX; ty=e.touches[0].clientY; }}
  }}, {{passive:true}});
  document.getElementById('map').addEventListener('touchend', e => {{
    if(e.changedTouches.length!==1) return;
    const t=e.changedTouches[0];
    if(Math.abs(t.clientX-tx)>12 || Math.abs(t.clientY-ty)>12) return;
    const r=document.getElementById('map').getBoundingClientRect();
    const g=map.unproject(t.clientX-r.left, t.clientY-r.top); if(!g) return;
    drop(g.latitude, g.longitude);
    ctxt.textContent = g.latitude.toFixed(5)+', '+g.longitude.toFixed(5);
    coord.style.display = 'block';
    window.parent.postMessage({{type:'osm_pin', lat:g.latitude, lon:g.longitude}}, '*');
  }}, {{passive:true}});
}}
</script></body></html>"""

    components.html(html, height=660)

    qp = st.query_params
    try:
        if "cam_rot" in qp:
            new_rot = float(qp["cam_rot"])
            if abs(new_rot - st.session_state.get("cam3d_rot", 0)) > 0.5:
                st.session_state["cam3d_rot"] = new_rot
        if "cam_tilt" in qp:
            new_tilt = float(qp["cam_tilt"])
            if abs(new_tilt - st.session_state.get("cam3d_tilt", 45)) > 0.5:
                st.session_state["cam3d_tilt"] = new_tilt
    except (ValueError, TypeError):
        pass


# ─────────────────────────────────────────────────────────────────────────────
def render_3d_map_component(lat, lon, radius_meters, path_data, animate_trigger,
                             sim_time, m_slat, m_slon, m_el, rise_time, set_time,
                             init_rot=0, init_tilt=45, init_zoom=1.3):
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

    cx  = round((m_slon - lon) * 111111 * cos_lat, 2)
    cz  = round(-(m_slat - lat) * 111111, 2)
    cy  = round(max(0, m_el) * (R / 90.0) * 2.2, 2)
    ct  = sim_time.strftime('%H:%M')
    cd  = int(R * 2.2)
    ch  = int(R * 1.3)

    import math as _m
    init_theta = _m.pi / 4 - _m.radians(float(init_rot))
    init_phi   = max(0.15, min(_m.pi / 2.1, _m.radians(90.0 - float(init_tilt))))
    init_cr    = int(R * max(0.6, min(4.0, float(init_zoom))))

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
cv.width=W; cv.height=H;
const rend=new THREE.WebGLRenderer({{canvas:cv,antialias:true}});
rend.setPixelRatio(Math.min(devicePixelRatio,2));
rend.setSize(W,H);
rend.shadowMap.enabled=true;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x0A0C10);
scene.fog=new THREE.FogExp2(0x0A0C10,0.0007);
const cam=new THREE.PerspectiveCamera(50,W/H,0.5,8000);
cam.position.set({cd},{ch},{cd}); cam.lookAt(0,0,0);
scene.add(new THREE.AmbientLight(0xffffff,0.35));
const dl=new THREE.DirectionalLight(0xffd580,1.8);
dl.position.set(300,600,300); dl.castShadow=true; scene.add(dl);
const R={R};

scene.add(new THREE.Mesh(
  new THREE.CylinderGeometry(R,R,3,80),
  new THREE.MeshLambertMaterial({{color:0x0D1118}})));
scene.add(new THREE.GridHelper(R*2,Math.max(10,Math.round(R/13)),0x151C28,0x0F1520));
scene.add(new THREE.Mesh(new THREE.TorusGeometry(R,2.5,8,80),
  new THREE.MeshBasicMaterial({{color:0x1A2535}})));
const lm=new THREE.LineBasicMaterial({{color:0x1A2535}});
[[[-R,0],[R,0]],[[0,-R],[0,R]]].forEach(([a,b])=>
  scene.add(new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(a[0],1,a[1]),
      new THREE.Vector3(b[0],1,b[1])]),lm)));

const pil=new THREE.Mesh(
  new THREE.CylinderGeometry(5.5,5.5,18,16),
  new THREE.MeshLambertMaterial({{color:0xF39C12}}));
pil.position.y=9; scene.add(pil);
scene.add(new THREE.Mesh(new THREE.TorusGeometry(11,2,8,32),
  new THREE.MeshBasicMaterial({{color:0xF39C12,transparent:true,opacity:.35}})));

function spr(txt,col){{
  const cv2=document.createElement('canvas'); cv2.width=128; cv2.height=64;
  const c2=cv2.getContext('2d');
  c2.fillStyle=col; c2.font='bold 34px JetBrains Mono,monospace';
  c2.textAlign='center'; c2.textBaseline='middle'; c2.fillText(txt,64,32);
  const sp=new THREE.Sprite(new THREE.SpriteMaterial(
    {{map:new THREE.CanvasTexture(cv2),transparent:true,depthTest:false}}));
  sp.scale.set(48,24,1); return sp;
}}
const ld=R+52;
[['N','#E74C3C',0,-ld],['S','#2D3748',0,ld],
 ['E','#2D3748',ld,0], ['W','#2D3748',-ld,0]].forEach(([t,c,x,z])=>{{
  const s=spr(t,c); s.position.set(x,8,z); scene.add(s);
}});

const pd={pts_js};
const ap=pd.filter(p=>p.el>=0).map(p=>new THREE.Vector3(p.x,p.y,p.z));
if(ap.length>1){{
  const cv3=new THREE.CatmullRomCurve3(ap);
  scene.add(new THREE.Mesh(
    new THREE.TubeGeometry(cv3,ap.length*3,3,8,false),
    new THREE.MeshBasicMaterial({{color:0xF39C12,transparent:true,opacity:.82}})));
}}

pd.filter(p=>p.el>=0).forEach((p,i)=>{{
  if(i%4!==0) return;
  const col=new THREE.Color().setHSL(.09-(i/pd.length)*.04,1,.55);
  const d=new THREE.Mesh(new THREE.SphereGeometry(3.5,8,8),
    new THREE.MeshBasicMaterial({{color:col}}));
  d.position.set(p.x,p.y,p.z); scene.add(d);
}});

pd.filter(p=>p.el>=0).forEach((p,i)=>{{
  if(i%7!==0) return;
  const g=new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(p.x,0,p.z),new THREE.Vector3(p.x,p.y,p.z)]);
  scene.add(new THREE.Line(g,
    new THREE.LineBasicMaterial({{color:0x2D1B00,transparent:true,opacity:.35}})));
}});

const sunCanvas=document.createElement('canvas');
sunCanvas.width=128; sunCanvas.height=128;
const sunCtx=sunCanvas.getContext('2d');
sunCtx.font='96px serif';
sunCtx.textAlign='center'; sunCtx.textBaseline='middle';
sunCtx.fillText('☀️',64,64);
const sunTex=new THREE.CanvasTexture(sunCanvas);
const sm=new THREE.Sprite(new THREE.SpriteMaterial(
  {{map:sunTex,transparent:true,depthTest:false}}));
sm.scale.set(60,60,1);
scene.add(sm);

const sg=[new THREE.Vector3(0,0,0),new THREE.Vector3(0,0,0)];
const sgeo=new THREE.BufferGeometry().setFromPoints(sg);
scene.add(new THREE.Line(sgeo,
  new THREE.LineBasicMaterial({{color:0x374151,transparent:true,opacity:.5}})));

function setSun(x,y,z,t,el){{
  const yy=Math.max(0,y);
  sm.position.set(x,yy,z);
  const s=sgeo.attributes.position;
  s.setXYZ(0,0,.5,0);
  s.setXYZ(1,x===0?0:-x*2,.5,z===0?0:-z*2);
  s.needsUpdate=true;
  document.getElementById('hel').textContent=el.toFixed(1)+'°';
  document.getElementById('htm').textContent=t;
  document.getElementById('stm').textContent=t;
  sm.visible=el>=-2;
}}
setSun({cx},{cy},{cz},'{ct}',{m_el});

let ai=0;
if({'true' if animate_trigger else 'false'}){{
  setInterval(()=>{{
    const p=pd[ai]; setSun(p.x,p.y,p.z,p.time,p.el);
    ai=(ai+1)%pd.length;
  }},160);
}}

let drag=false, prev={{x:0,y:0}};
let th={init_theta:.4f};
let ph={init_phi:.4f};
let cr={init_cr};

function uCam(){{
  cam.position.set(
    cr*Math.sin(ph)*Math.sin(th),
    cr*Math.cos(ph),
    cr*Math.sin(ph)*Math.cos(th));
  cam.lookAt(0,0,0);
}}
uCam();

cv.addEventListener('mousedown',e=>{{ drag=true; prev={{x:e.clientX,y:e.clientY}}; }});
cv.addEventListener('mouseup',  ()=>drag=false);
cv.addEventListener('mousemove',e=>{{
  if(!drag) return;
  th -= (e.clientX-prev.x)*.005;
  ph  = Math.max(.15,Math.min(Math.PI/2.1,ph+(e.clientY-prev.y)*.005));
  prev={{x:e.clientX,y:e.clientY}}; uCam();
}});
cv.addEventListener('wheel',e=>{{
  cr=Math.max(R*.6,Math.min(R*4,cr+e.deltaY*.4)); uCam(); e.preventDefault();
}},{{passive:false}});
let lt=null;
cv.addEventListener('touchstart',e=>lt=e.touches[0]);
cv.addEventListener('touchmove',e=>{{
  if(!lt) return;
  const t=e.touches[0];
  th-=(t.clientX-lt.clientX)*.005;
  ph=Math.max(.15,Math.min(Math.PI/2.1,ph+(t.clientY-lt.clientY)*.005));
  lt=t; uCam(); e.preventDefault();
}},{{passive:false}});

(function loop(){{ requestAnimationFrame(loop); rend.render(scene,cam); }})();
</script></body></html>"""
    components.html(html, height=620)


def render_live_component(lat, lon, radius_meters, path_data, animate_trigger,
                          sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
                          rise_edge, set_edge, rise_time, set_time,
                          init_view='3d', init_rot=0, init_tilt=0, init_zoom=1.3):
    if init_view == '3d':
        render_3d_shadow_component(
            lat, lon, radius_meters, path_data, animate_trigger,
            sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
            rise_time, set_time,
            allow_location_select=False,
            init_rot=init_rot, init_tilt=init_tilt, init_zoom=init_zoom
        )
    else:
        render_map_component(
            lat, lon, radius_meters, path_data, animate_trigger,
            sim_time, m_slat, m_slon, m_shlat, m_shlon, m_el, m_az,
            rise_edge, set_edge, rise_time, set_time, "Off"
        )
