import streamlit as st
import requests
import json
import time
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation

SERVER_URL = "http://localhost:8000" 

VIT_LOCATIONS = {
    "AB1": [12.843478, 80.153042],
    "AB2_SJT": [12.843026, 80.156419],
    "AB3": [12.843674, 80.154511],
    "CENTRAL_LIBRARY": [12.841182, 80.154015],
    "MAIN_GATE": [12.840616, 80.153185],
    "GUEST_HOUSE": [12.840902, 80.153221],
    "MBA_AMPHITHEATER": [12.841325, 80.154074],
    "CLOCK_COURT": [12.841262, 80.154588],
    "MGR_STATUE": [12.841704, 80.154077],
    "VMART": [12.844651, 80.153743],
    "NORTH_SQUARE": [12.844207, 80.154062],
    "VIT_GYM": [12.843737, 80.152516],
    "HEALTH_CENTRE": [12.841619, 80.156539],
    "SWIMMING_POOL": [12.840986, 80.156370],
    "PARKING_AREA": [12.841530, 80.153098],
    "STUDENT_PARKING_3": [12.841975, 80.151912],
    "CAR_PARKING": [12.845097, 80.153050],
    "CRICKET_GROUND": [12.842268, 80.154879]
}

st.set_page_config(page_title="VITC EV Dispatch Portal", page_icon="🚐")
st.title("VIT Chennai EV Dispatch Portal")

def render_student_map(center_lat, center_lon, fleet_data, zoom=18):
    locs_json = json.dumps(VIT_LOCATIONS)
    fleet_json = json.dumps(fleet_data)
    
    leaflet_html = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="map" style="height: 480px; width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"></div>
    <script>
        var map = L.map('map').setView([{center_lat}, {center_lon}], {zoom});
        L.tileLayer('http://{{s}}.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
            attribution: '© Google Maps'
        }}).addTo(map);
        
        // Student Marker
        L.marker([{center_lat}, {center_lon}]).addTo(map).bindPopup('<b>Your Pickup Point</b>').openPopup();

        // Render Live Fleet (Buses and EVs)
        var fleet = {fleet_json};
        for (var id in fleet) {{
            var v = fleet[id];
            var icon = (v.category === 'BUS') ? '🚌' : '🚐';
            var color = (v.category === 'BUS') ? '#e67e22' : '#2ecc71';
            
            L.marker([v.lat, v.lon], {{
                icon: L.divIcon({{
                    className: 'fleet-icon',
                    html: '<div style="font-size: 24px; filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.3));">' + icon + '</div>',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                }})
            }}).addTo(map).bindPopup("<b>" + id + "</b><br>Status: " + v.status);
        }}
            
        // Render Landmarks
        var locations = {locs_json};
        for (var name in locations) {{
            var coords = locations[name];
            L.circle([coords[0], coords[1]], {{
                color: '#1f6feb', fillColor: '#1f6feb', fillOpacity: 0.1, radius: 8
            }}).addTo(map).bindPopup("<b>" + name.replace(/_/g, " ") + "</b>");
        }}
    </script>
    """
    components.html(leaflet_html, height=500)

fleet_data = {}
try:
    response = requests.get(f"{SERVER_URL}/get_fleet")
    if response.status_code == 200:
        fleet_data = response.json()
except:
    st.error("Cannot connect to Fleet Server. Live tracking disabled.")

st.info("Live tracking is active. Moving buses (🚌) and EVs (🚐) are shown on the map.")
mode = st.radio("Location Mode:", ["Select Building", "Use Live GPS"], horizontal=True)

lat, lon = None, None
if mode == "Select Building":
    sel = st.selectbox("Choose Pickup Building:", list(VIT_LOCATIONS.keys()))
    lat, lon = VIT_LOCATIONS[sel]
else:
    loc = get_geolocation()
    if loc: lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    else: st.warning("Enable GPS permissions.")

if lat and lon:
    render_student_map(lat, lon, fleet_data)
    if st.button("🚀 Call Nearest EV", use_container_width=True):
        try:
            resp = requests.post(f"{SERVER_URL}/call_ev", params={"student_lat": lat, "student_lon": lon})
            if resp.status_code == 200: st.success("Success! EV is dispatched."); st.balloons()
            else: st.error("No idle EVs.")
        except: st.error("Backend server offline.")

time.sleep(5)
st.rerun()
