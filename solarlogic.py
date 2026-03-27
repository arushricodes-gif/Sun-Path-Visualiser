import math
import requests
import streamlit as st
from astral.sun import azimuth, elevation


def search_city(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'SolarPathVisualizer_v1'}
        resp = requests.get(url, headers=headers).json()
        if resp:
            return [float(resp[0]['lat']), float(resp[0]['lon'])]
    except:
        return None
    return None


@st.cache_data(ttl=600)
def get_environmental_data(lat, lon):
    api_key = "d4b056a2-a4bc-48d0-9a38-3f5a2c675ea7"
    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
    env = {
        "aqi": "N/A", "temp": "N/A", "hum": "N/A", "wind": "N/A",
        "color": "#444", "label": "Unknown",
        "wind_dir": None, "wind_name": "N/A"
    }
    try:
        r = requests.get(url, timeout=5).json()
        if r.get("status") == "success":
            data = r["data"]["current"]
            env.update({
                "aqi":  data["pollution"]["aqius"],
                "temp": data["weather"]["tp"],
                "hum":  data["weather"]["hu"],
                "wind": data["weather"]["ws"],
            })
            aqi = env["aqi"]
            if   aqi <= 50:  env["label"], env["color"] = "Good",        "#00e400"
            elif aqi <= 100: env["label"], env["color"] = "Moderate",    "#ffff00"
            elif aqi <= 150: env["label"], env["color"] = "Unhealthy(S)","#ff7e00"
            else:            env["label"], env["color"] = "Unhealthy",   "#ff0000"
    except:
        pass
    return env


def get_solar_pos(city_info, t, r, clat, clon):
    az_val = azimuth(city_info.observer, t)
    el_val = elevation(city_info.observer, t)
    sc     = math.cos(math.radians(max(0, el_val)))
    slat   = clat + (r * sc / 111111) * math.cos(math.radians(az_val))
    slon   = clon + (r * sc / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az_val))
    shlat  = clat + (r * 0.7 / 111111) * math.cos(math.radians(az_val + 180))
    shlon  = clon + (r * 0.7 / (111111 * math.cos(math.radians(clat)))) * math.sin(math.radians(az_val + 180))
    return slat, slon, shlat, shlon, az_val, el_val


def get_edge(lat, lon, az_input, radius):
    rad = math.radians(az_input)
    return [
        lat + (radius / 111111) * math.cos(rad),
        lon + (radius / (111111 * math.cos(math.radians(lat)))) * math.sin(rad)
    ]


def calculate_solar_radiation(elevation_deg):
    if elevation_deg <= 0:
        return 0
    el_rad       = math.radians(elevation_deg)
    air_mass     = 1 / (math.sin(el_rad) + 0.001)
    I0           = 1367
    transmission = 0.7 ** (air_mass ** 0.678)
    return round(I0 * math.sin(el_rad) * transmission, 2)


# ── OSM Building Obstruction ──────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nearby_buildings(lat, lon, radius_m=200):
    """
    Returns (buildings_list, osm_ok).
    osm_ok=False means network/parse failed — caller must show fallback UI.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
[out:json][timeout:15];
(
  way["building"](around:{radius_m},{lat},{lon});
  relation["building"](around:{radius_m},{lat},{lon});
);
out center tags;
"""
    try:
        resp = requests.post(overpass_url, data={"data": query}, timeout=18)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return [], False

    cos_lat   = math.cos(math.radians(lat))
    buildings = []

    for el in data.get("elements", []):
        center = el.get("center")
        if not center:
            continue
        blat, blon = center["lat"], center["lon"]
        dlat_m = (blat - lat) * 111111
        dlon_m = (blon - lon) * 111111 * cos_lat
        dist_m = math.sqrt(dlat_m ** 2 + dlon_m ** 2)
        if dist_m < 2:
            continue
        bearing = math.degrees(math.atan2(dlon_m, dlat_m)) % 360
        tags   = el.get("tags", {})
        height = None
        if "height" in tags:
            try:
                height = float(str(tags["height"]).replace("m", "").strip())
            except ValueError:
                pass
        if height is None and "building:levels" in tags:
            try:
                height = float(tags["building:levels"]) * 3.5
            except ValueError:
                pass
        if height is None:
            height = 10.0
        obs_angle = math.degrees(math.atan2(height, dist_m))
        buildings.append({
            "dist_m":        round(dist_m, 1),
            "bearing_deg":   round(bearing, 1),
            "height_m":      round(height, 1),
            "obs_angle_deg": round(obs_angle, 2),
        })

    return buildings, True


def floor_elevation_m(floor_number):
    if floor_number == 0:
        return 1.5
    return floor_number * 3.5 + 1.5


def make_synthetic_buildings(surround_height_m, surround_dist_m=20):
    obs_angle = math.degrees(math.atan2(surround_height_m, surround_dist_m))
    return [
        {
            "dist_m":        surround_dist_m,
            "bearing_deg":   float(i * 10),
            "height_m":      float(surround_height_m),
            "obs_angle_deg": round(obs_angle, 2),
        }
        for i in range(36)
    ]


def get_obstruction_angle(buildings, sun_az, floor_m, angular_width_deg=30):
    if not buildings:
        return 0.0
    max_needed = 0.0
    for b in buildings:
        diff = abs((b["bearing_deg"] - sun_az + 180) % 360 - 180)
        if diff > angular_width_deg:
            continue
        effective_height = b["height_m"] - floor_m
        if effective_height <= 0:
            continue
        obs_angle = math.degrees(math.atan2(effective_height, b["dist_m"]))
        if obs_angle > max_needed:
            max_needed = obs_angle
    return round(max_needed, 2)


def is_sun_visible(buildings, sun_az, sun_el, floor_m, angular_width_deg=30):
    if sun_el <= 0:
        return False
    return sun_el > get_obstruction_angle(buildings, sun_az, floor_m, angular_width_deg)


def compute_sunlight_window(city_info, obs_date, local_tz, buildings, floor_m,
                            radius_meters, lat, lon, step_minutes=5):
    from astral.sun import sunrise, sunset, noon
    from datetime import datetime, timedelta

    try:
        r_t = sunrise(city_info.observer, date=obs_date, tzinfo=local_tz)
        s_t = sunset(city_info.observer,  date=obs_date, tzinfo=local_tz)
        n_t = noon(city_info.observer,    date=obs_date, tzinfo=local_tz)
    except Exception:
        return None

    sun_start = sun_end = None
    peak_el   = -90.0
    peak_time = ""
    lit_mins  = 0

    curr    = r_t - timedelta(minutes=30)
    day_end = s_t + timedelta(minutes=30)

    while curr <= day_end:
        _, _, _, _, az_v, el_v = get_solar_pos(city_info, curr, radius_meters, lat, lon)
        if el_v > peak_el:
            peak_el, peak_time = el_v, curr.strftime("%H:%M")
        if is_sun_visible(buildings, az_v, el_v, floor_m):
            if sun_start is None:
                sun_start = curr
            sun_end  = curr
            lit_mins += step_minutes
        curr += timedelta(minutes=step_minutes)

    hourly = []
    for h in range(6, 21):
        t = local_tz.localize(
            datetime.combine(obs_date, datetime.min.time())
        ) + timedelta(hours=h, minutes=30)
        _, _, _, _, az_v, el_v = get_solar_pos(city_info, t, radius_meters, lat, lon)
        needed = get_obstruction_angle(buildings, az_v, floor_m)
        hourly.append({
            "hour":      h,
            "el":        round(el_v, 1),
            "needed_el": needed,
            "lit":       (el_v > needed) if el_v > 0 else False,
        })

    return {
        "rise":        r_t.strftime("%H:%M"),
        "set":         s_t.strftime("%H:%M"),
        "noon":        n_t.strftime("%H:%M"),
        "sun_start":   sun_start.strftime("%H:%M") if sun_start else None,
        "sun_end":     sun_end.strftime("%H:%M")   if sun_end   else None,
        "sun_minutes": lit_mins,
        "peak_el":     round(peak_el, 1),
        "peak_time":   peak_time,
        "hourly":      hourly,
    }
                                
