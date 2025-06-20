import requests
from config import AXIFLEET_API_KEY

url = "https://online.axifleet.ro/api/history/unread/list"

headers = {
    "Content-Type": "application/json",
    "Cookie": f"session_key={AXIFLEET_API_KEY}"
}

data = {
    "from": "2025-06-01T00:00:00.000Z",
    "limit": 100,
    "hash": AXIFLEET_API_KEY
}

response = requests.post(url, json=data, headers=headers)

if response.ok:
    print("Răspuns primit:")
    print(response.json())
else:
    print(f"Eroare: {response.status_code} – {response.text}")
