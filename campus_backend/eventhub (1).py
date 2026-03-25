import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

url = "https://122.184.65.205/EventHub/"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Host": "eventhubcc.vit.ac.in"
}

r = requests.get(url, headers=headers, verify=False)

soup = BeautifulSoup(r.text, "html.parser")

cards = soup.select(".card")

events = []

for card in cards:

    title = card.select_one(".card-title span").get_text(strip=True)

    date = card.select_one("i.fa-calendar-days").find_next("span").get_text(strip=True)

    location = card.select_one("i.fa-map-location-dot").find_next("span").get_text(strip=True)

    eid = card.select_one("button[name='eid']")["value"]

    events.append({
        "title": title,
        "date": date,
        "location": location,
        "event_id": eid
    })

from datetime import date

today = str(date.today())

today_events = [e for e in events if e["date"] == today]

import json

with open("today_events.json","w") as f:
    json.dump(today_events, f, indent=4)