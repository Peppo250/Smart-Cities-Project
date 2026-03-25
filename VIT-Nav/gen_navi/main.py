import os
import logging
from typing import List, Tuple, Dict

import networkx as nx
import osmnx as ox
from pyproj import Transformer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import difflib

GRAPH_FILENAME = "vit_chennai.graphml"
CAMPUS_CENTER = (12.8406, 80.1534) 
SEARCH_RADIUS_METERS = 1500
NETWORK_TYPE = "walk"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("campus-navigator")

log.info("Loading routing graph...")
if not os.path.exists(GRAPH_FILENAME):
    log.info(f"{GRAPH_FILENAME} not found — downloading graph from OSM (this may take a while)...")
    graph = ox.graph_from_point(
        CAMPUS_CENTER,
        dist=SEARCH_RADIUS_METERS,
        network_type="walk",
        custom_filter='["highway"~"footway|path|pedestrian|living_street|service"]'
    )
    graph = ox.distance.add_edge_lengths(graph)
    ox.save_graphml(graph, GRAPH_FILENAME)
    log.info(f"Graph downloaded and saved to {GRAPH_FILENAME}")
else:
    graph = ox.load_graphml(GRAPH_FILENAME)
    try:
        graph = ox.distance.add_edge_lengths(graph)
    except Exception as e:
        log.warning("Could not call ox.distance.add_edge_lengths: %s", e)

log.info("Graph loaded: %d nodes, %d edges", graph.number_of_nodes(), graph.number_of_edges())

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
ORIGIN_X, ORIGIN_Y = transformer.transform(CAMPUS_CENTER[1], CAMPUS_CENTER[0])

def get_3d(lat: float, lon: float) -> Tuple[float, float]:
    x, y = transformer.transform(lon, lat)
    return (x - ORIGIN_X, y - ORIGIN_Y)

log.info("Extracting named POIs (buildings/amenities) around campus from OSM...")
LOCATIONS: Dict[str, Tuple[float, float]] = {}
try:
    tags = {"building": True, "amenity": True, "name": True}
    pois = ox.geometries_from_point(CAMPUS_CENTER, tags=tags, dist=SEARCH_RADIUS_METERS)
except Exception as e:
    log.warning("ox.geometries_from_point failed (%s), trying features_from_point fallback", e)
    try:
        pois = ox.features_from_point(CAMPUS_CENTER, tags=tags, dist=SEARCH_RADIUS_METERS)
    except Exception as e2:
        log.error("Could not fetch POIs from OSM: %s", e2)
        pois = None

if pois is not None and not pois.empty:
    for _, row in pois.iterrows():
        name = row.get("name")
        if not name or not isinstance(name, str):
            continue
        geom = row.get("geometry")
        if geom is None:
            continue
        try:
            centroid = geom.centroid
            lat, lon = float(centroid.y), float(centroid.x)
            if name not in LOCATIONS:
                LOCATIONS[name] = (lat, lon)
        except Exception:
            continue

log.info("Extracted %d named POIs from OSM", len(LOCATIONS))

if not LOCATIONS:
    log.warning("No POIs extracted — falling back to a small built-in set")
    LOCATIONS = {
        "ADMIN_BLOCK": (12.8406, 80.1534),
        "CENTRAL_LIBRARY": (12.8401, 80.1538),
        "GAZEBO_CANTEEN": (12.8398, 80.1532),
        "SPORTS_COMPLEX": (12.8435, 80.1535),
        "HEALTH_CENTRE": (12.8405, 80.1528),
    }

def nearest_node_for_point(lat: float, lon: float):
    try:
        return ox.nearest_nodes(graph, X=lon, Y=lat)
    except Exception as e:
        try:
            return ox.distance.nearest_nodes(graph, X=lon, Y=lat)
        except Exception:
            raise

def route_length_meters(route: List[int]) -> float:
    total = 0.0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = graph.get_edge_data(u, v)
        if not edge_data:
            continue
        try:
            first_edge = next(iter(edge_data.values()))
        except Exception:
            first_edge = edge_data
        seg_len = first_edge.get("length", 0) or 0
        total += float(seg_len)
    return total

def generate_gps_path(route: List[int]) -> List[Tuple[float, float]]:
    path = []
    for n in route:
        node = graph.nodes[n]
        lat = node.get("y")  
        lon = node.get("x") 
        path.append((lat, lon))
    return path

def generate_directions_simple(route: List[int]) -> List[dict]:
    steps = []
    for u, v in zip(route[:-1], route[1:]):
        edge_data = graph.get_edge_data(u, v)
        if edge_data:
            try:
                edge = next(iter(edge_data.values()))
            except Exception:
                edge = edge_data
            seg_len = float(edge.get("length", 0) or 0)
        else:
            seg_len = 0.0
        steps.append({
            "from": (graph.nodes[u]["y"], graph.nodes[u]["x"]),
            "to": (graph.nodes[v]["y"], graph.nodes[v]["x"]),
            "meters": round(seg_len, 2)
        })
    return steps

app = FastAPI(title="Campus Navigator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

class NavigationResponse(BaseModel):
    destination: str
    gps_path: List[Tuple[float, float]]
    path_3d: List[Tuple[float, float]]
    distance_meters: float
    eta_minutes: float
    directions: List[dict]

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/locations")
async def locations():
    return {"count": len(LOCATIONS), "locations": list(LOCATIONS.keys())}

@app.get("/search")
async def search(query: str, max_results: int = 10):
    names = list(LOCATIONS.keys())
    matches = difflib.get_close_matches(query, names, n=max_results, cutoff=0.4)
    return {"query": query, "matches": matches}

@app.get("/navigate", response_model=NavigationResponse)
async def navigate(tag_id: str, lat: float, lon: float, dest: str):
    if dest not in LOCATIONS:
        candidates = difflib.get_close_matches(dest, list(LOCATIONS.keys()), n=1, cutoff=0.4)
        if candidates:
            dest_name = candidates[0]
        else:
            raise HTTPException(status_code=404, detail=f"Destination '{dest}' not found")
    else:
        dest_name = dest

    dest_lat, dest_lon = LOCATIONS[dest_name]

    try:
        orig_node = nearest_node_for_point(lat, lon)
        dest_node = nearest_node_for_point(dest_lat, dest_lon)

        route = nx.shortest_path(graph, orig_node, dest_node, weight="length")

        gps_path = generate_gps_path(route)
        distance = route_length_meters(route)
        path_3d = [get_3d(pt[0], pt[1]) for pt in gps_path]
        directions = generate_directions_simple(route)
        eta_minutes = round((distance / 1.4) / 60, 1)

        return {
            "destination": dest_name,
            "gps_path": gps_path,
            "path_3d": path_3d,
            "distance_meters": round(distance, 2),
            "eta_minutes": eta_minutes,
            "directions": directions
        }
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=400, detail="No path found between these points.")
    except Exception as e:
        log.exception("Unexpected error in navigation")
        raise HTTPException(status_code=500, detail=str(e))