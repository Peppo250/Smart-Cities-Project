import streamlit as st
import requests
import time
import json
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation

SERVER_URL = "http://localhost:8000" 

VIT_LOCATIONS = {
    "AB1": [12.84347818569651, 80.15304198584788],
    "AB2_SJT": [12.843026329542724, 80.15641964968837],
    "AB3": [12.843674318319481, 80.15451183638832],
    "CENTRAL_LIBRARY": [12.841182458853275, 80.15401530671869],
    "MAIN_GATE": [12.840615842783512, 80.15318490565902],
    "GUEST_HOUSE": [12.840901545849901, 80.15322111548585],
    "MBA_AMPHITHEATER": [12.84132519646897, 80.15407405794888],
    "CLOCK_COURT": [12.841262433461138, 80.15458770097428],
    "MGR_STATUE": [12.841704389325017, 80.15407674016363],
    "VMART": [12.844651167237494, 80.15374321467853],
    "NORTH_SQUARE": [12.844206601468189, 80.15406239754654],
    "VIT_GYM": [12.84373708072442, 80.15251627289408],
    "HEALTH_CENTRE": [12.841619184612885, 80.15653926540992],
    "SWIMMING_POOL": [12.840986324278141, 80.15637028623946],
    "PARKING_AREA": [12.841530270446556, 80.15309799124007],
    "STUDENT_PARKING_3": [12.841974840954315, 80.15191245486481],
    "CAR_PARKING": [12.845097272869918, 80.15304971147641],
    "CRICKET_GROUND": [12.842267734048432, 80.1548789780203]
}

def get_location_name(lat, lon):
    for n, c in VIT_LOCATIONS.items():
        if abs(c[0] - lat) < 0.00015 and abs(c[1] - lon) < 0.00015: return n.replace("_", " ")
    return f"GPS ({lat:.5f}, {lon:.5f})"

def render_google_roadmap(driver_lat, driver_lon, pickup_lat=None, pickup_lon=None, route_path=None):
    driver_marker = f"L.marker([{driver_lat}, {driver_lon}], {{icon: L.divIcon({{className: 'custom-div-icon', html: '🚐', iconSize: [32, 42], iconAnchor: [16, 42]}})}}).addTo(map).bindPopup('<b>You are here</b>');"
    pickup_marker = ""
    if pickup_lat and pickup_lon:
        pickup_marker = f"L.marker([{pickup_lat}, {pickup_lon}]).addTo(map).bindPopup('<b>Pick up Student Here</b>').openPopup();"
    polyline_js = ""
    if route_path and len(route_path) > 1:
        polyline_js = f"L.polyline({json.dumps(route_path)}, {{color: '#ff3333', weight: 6, opacity: 0.8, dashArray: '5, 10'}}).addTo(map);"

    leaflet_html = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="map" style="height: 450px; width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);"></div>
    <script>
        var map = L.map('map').setView([{driver_lat}, {driver_lon}], 17);
        L.tileLayer('http://{{s}}.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'], attribution: '© Google Maps'
        }}).addTo(map);
        {driver_marker} {pickup_marker} {polyline_js}
    </script>
    """
    components.html(leaflet_html, height=470)

st.set_page_config(page_title="VITC Driver App", page_icon="🚐", layout="centered")
st.title("VIT Chennai Driver Portal")

category = st.radio("Driving Mode:", ["Electric Vehicle", "Shuttle Bus"], horizontal=True)
tag_id = st.selectbox("Assign Vehicle ID:", [f"EV_{i:02d}" for i in range(1, 6)] if category == "Electric Vehicle" else [f"BUS_{i:02d}" for i in range(1, 11)])

loc = get_geolocation()
if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    st.success(f"Tracking: **{tag_id}** at ({lat:.5f}, {lon:.5f})")
    if st.toggle("Go Online", value=True):
        try:
            resp = requests.post(f"{SERVER_URL}/update_location", params={"tag_id": tag_id, "lat": lat, "lon": lon})
            if resp.status_code == 200:
                data = resp.json()
                if data["status"] == "ON_PICKUP":
                    st.divider()
                    st.error("🚨 **NEW PICKUP REQUEST ASSIGNED!**")
                    target = data["target"]
                    st.metric(label="Destination", value=get_location_name(target['lat'], target['lon']))
                    render_google_roadmap(lat, lon, target['lat'], target['lon'], data.get("route_path", []))
                    if st.button("Complete Pickup", use_container_width=True):
                        requests.post(f"{SERVER_URL}/complete_task", params={"tag_id": tag_id})
                        st.balloons()
                else:
                    st.info("📡 **System Online**: Waiting for requests...")
                    render_google_roadmap(lat, lon)
        except: st.error("Server connection failed.")
else: st.warning("GPS must be enabled.")
time.sleep(5)
st.rerun()
