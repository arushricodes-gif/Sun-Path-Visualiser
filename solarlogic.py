import math
import requests
import streamlit as st
from astral.sun import azimuth, elevation

def search_city(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'SolarPathVisualizer_v1'}
        resp = requests.get(url, headers=headers).json()
        if resp: return [float(resp[0]['lat']), float(resp[0]['lon'])]
    except: return None
    return None

@st.cache_data(ttl=600)
def get_environmental_data(lat, lon):
    api_key = "d4b056a2-a4bc-48d0-9a38-3f5a2c675ea7"
    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
    # Default values to prevent dashboard errors
    env = {"aqi": "N/A", "temp": "N/A", "hum": "N/A", "wind": "N/A", "color": "#444", "label": "Unknown"}
    try:
        r = requests.get(url, timeout=5).json()
        if r.get("status") == "success":
            data = r["data"]["current"]
            env.update({"aqi": data["pollution"]["aqius"], "temp": data["weather"]["tp"], "hum": data["weather"]["hu"], "wind": data["weather"]["ws"]})
            aqi = env["aqi"]
            if aqi <= 50: env["label"], env["color"] = "Good", "#00e400"
            elif aqi <= 100: env["label"], env["color"] = "Moderate", "#ffff00"
            elif aqi <= 150: env["label"], env["color"] = "Unhealthy(S)", "#ff7e00"
            else: env["label"], env["color"] = "Unhealthy", "#ff0000"
    except: pass
    return env

def get_solar_pos(city_info, t, r, clat, clon):
    az_val = azimuth(city_info.observer, t)
    el_val = elevation(city_info.observer, t)
    sc = math.cos(math.radians(max(0, el_val)))
    slat = clat + (r * sc / 111111) * math.cos(math.radians(az_val))
    slon = clon + (r * sc / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az_val))
    shlat = clat + (r * 0.7 / 111111) * math.cos(math.radians(az_val + 180))
    shlon = clon + (r * 0.7 / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az_val + 180))
    return slat, slon, shlat, shlon, az_val, el_val

def get_edge(lat, lon, az_input, radius):
    rad = math.radians(az_input)
    return [lat + (radius/111111)*math.cos(rad), lon + (radius/(111111*math.cos(math.radians(lat))))*math.sin(rad)]


