import requests
from config import AXIFLEET_API_KEY

url = "https://online.axifleet.ro/api/history/unread/list"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {AXIFLEET_API_KEY}"
}

response = requests.post(url, headers=headers, json={})

if response.status_code == 200:
    data = response.json()
    if "list" in data and len(data["list"]) > 0:
        print("✅ Conexiune reușită! Iată primul tracker găsit:\n")
        first = data["list"][0]
        label = first.get("extra", {}).get("tracker_label", "Fără etichetă")
        lat = first.get("location", {}).get("lat")
        lng = first.get("location", {}).get("lng")
        addr = first.get("location", {}).get("address", "Fără adresă")
        print(f"{label}: {lat}, {lng} — {addr}")
    else:
        print("⚠️ Conexiunea a mers, dar nu ai date în acest moment.")
else:
    print(f"❌ Eroare la conectare: {response.status_code} – {response.text}")
