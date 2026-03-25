from fastapi import FastAPI
from services.events import get_events
from services.parking import get_parking_status
from services.laundry import get_laundry_status
from services.static_data import get_static_data
app = FastAPI()
@app.get("/")
def home():
    return {"message": "Backend is running!"}
@app.get("/parking")
def parking():
    return get_parking_status()
@app.get("/events")
def events():
    return get_events()
@app.get("/laundry")
def laundry():
    return get_laundry_status()
@app.get("/static-data")
def static():
    return get_static_data()