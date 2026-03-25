import osmnx as ox
import networkx as nx
from pyproj import Transformer
from fastapi import FastAPI, HTTPException
from typing import Dict, Optional, List, Tuple
import os

# --- 1. GEOSPATIAL SETUP ---
CAMPUS_CENTER = (12.8417, 80.1540)

if os.path.exists("vit_chennai.graphml"):
    graph = ox.load_graphml("vit_chennai.graphml")
else:
    graph = ox.graph_from_point(CAMPUS_CENTER, dist=1000, network_type='all')
    ox.save_graphml(graph, "vit_chennai.graphml")

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
ORIGIN_X, ORIGIN_Y = transformer.transform(CAMPUS_CENTER[0], CAMPUS_CENTER[1])

# --- PAINSTAKINGLY FETCHED COORDINATES ---
VIT_LOCATIONS = {
    "AB1": (12.84347818569651, 80.15304198584788),
    "AB2_SJT": (12.843026329542724, 80.15641964968837),
    "AB3": (12.843674318319481, 80.15451183638832),
    "CENTRAL_LIBRARY": (12.841182458853275, 80.15401530671869),
    "MAIN_GATE": (12.840615842783512, 80.15318490565902),
    "GUEST_HOUSE": (12.840901545849901, 80.15322111548585),
    "MBA_AMPHITHEATER": (12.84132519646897, 80.15407405794888),
    "CLOCK_COURT": (12.841262433461138, 80.15458770097428),
    "MGR_STATUE": (12.841704389325017, 80.15407674016363),
    "VMART": (12.844651167237494, 80.15374321467853),
    "NORTH_SQUARE": (12.844206601468189, 80.15406239754654),
    "VIT_GYM": (12.84373708072442, 80.15251627289408),
    "HEALTH_CENTRE": (12.841619184612885, 80.15653926540992),
    "SWIMMING_POOL": (12.840986324278141, 80.15637028623946),
    "PARKING_AREA": (12.841530270446556, 80.15309799124007),
    "STUDENT_PARKING_3": (12.841974840954315, 80.15191245486481),
    "CAR_PARKING": (12.845097272869918, 80.15304971147641),
    "CRICKET_GROUND": (12.842267734048432, 80.1548789780203)
}

active_fleet: Dict[str, dict] = {}

def get_3d(lat, lon):
    x, y = transformer.transform(lat, lon)
    return (round(x - ORIGIN_X, 2), round(y - ORIGIN_Y, 2))

def get_gps_route(start_gps, end_gps):
    try:
        orig_node = ox.nearest_nodes(graph, X=start_gps[1], Y=start_gps[0])
        dest_node = ox.nearest_nodes(graph, X=end_gps[1], Y=end_gps[0])
        route = nx.shortest_path(graph, orig_node, dest_node, weight='length')
        return [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]
    except: return []

app = FastAPI()

@app.post("/update_location")
async def update_location(tag_id: str, lat: float, lon: float):
    cat = "BUS" if "BUS" in tag_id.upper() else "EV"
    if tag_id not in active_fleet: active_fleet[tag_id] = {"status": "IDLE", "target_gps": None}
    active_fleet[tag_id].update({"category": cat, "lat": lat, "lon": lon})
    r = []
    if active_fleet[tag_id]["status"] == "ON_PICKUP" and active_fleet[tag_id]["target_gps"]:
        t = active_fleet[tag_id]["target_gps"]
        r = get_gps_route((lat, lon), (t['lat'], t['lon']))
    return {"status": active_fleet[tag_id]["status"], "target": active_fleet[tag_id]["target_gps"], "route_path": r}

@app.get("/get_fleet")
async def get_fleet(): return active_fleet

@app.post("/call_ev")
async def call_ev(student_lat: float, student_lon: float):
    for tid, d in active_fleet.items():
        if d["category"] == "EV" and d["status"] == "IDLE":
            active_fleet[tid]["status"] = "ON_PICKUP"
            active_fleet[tid]["target_gps"] = {"lat": student_lat, "lon": student_lon}
            return {"message": "EV is on the way!", "vehicle_id": tid}
    raise HTTPException(status_code=404, detail="No available EVs.")

@app.post("/complete_task")
async def complete_task(tag_id: str):
    if tag_id in active_fleet:
        active_fleet[tag_id]["status"] = "IDLE"
        active_fleet[tag_id]["target_gps"] = None
        return {"status": "success"}
    raise HTTPException(status_code=404)
