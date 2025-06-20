import requests
from config import AXIFLEET_API_KEY
from datetime import datetime, timedelta

import requests
from config import AXIFLEET_API_KEY

import requests
from config import AXIFLEET_API_KEY
from datetime import datetime

def get_sensor_data_from_axifleet():
    url = "https://online.axifleet.ro/api/history/unread/list"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {AXIFLEET_API_KEY}"
    }

    body = {
        "limit": 100,
        "hash": AXIFLEET_API_KEY
    }

    response = requests.post(url, headers=headers, json=body)

    sensors = {}

    if response.status_code == 200:
        data = response.json()
        for item in data.get("list", []):
            location = item.get("location")
            if location and "lat" in location and "lng" in location:
                label = item.get("extra", {}).get("tracker_label", f"Tracker-{item.get('tracker_id', '???')}")
                timestamp_str = item.get("time")
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except:
                    timestamp = datetime.min

                if label not in sensors or timestamp > sensors[label]["timestamp"]:
                    sensors[label] = {
                        "SensorID": label,
                        "Latitude": location["lat"],
                        "Longitude": location["lng"],
                        "timestamp": timestamp,
                        "address": location.get("address", "Adresă necunoscută")
                    }
    else:
        print(f"Eroare: {response.status_code} – {response.text}")

    print(f"[DEBUG] Am extras {len(sensors)} senzori unici din API (cu locații cele mai recente)")
    return list(sensors.values())



