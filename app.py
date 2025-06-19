from flask import Flask, render_template, request
import googlemaps
from config import GOOGLE_MAPS_API_KEY
from geopy.distance import geodesic
import csv
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])

def index():
    report = []
    not_found = []

    if request.method == "POST":
        # Fișier adrese
        address_file = request.files["addresses"]
        addresses = []
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        reader = io.TextIOWrapper(address_file, encoding='utf-8')
        for line in reader:
            line = line.strip()
            if not line:
                continue
            try:
                result = gmaps.geocode(line)
                if result:
                    loc = result[0]["geometry"]["location"]
                    addresses.append((line, (loc["lat"], loc["lng"])))
                else:
                    not_found.append(line)
            except Exception as e:
                not_found.append(line)

        # Fișier senzori
        sensor_file = request.files["sensors"]
        reader = csv.DictReader(io.StringIO(sensor_file.read().decode('utf-8')))
        for row in reader:
            sensor_id = row["SensorID"]
            sensor_coord = (float(row["Latitude"]), float(row["Longitude"]))

            min_dist = float("inf")
            for _, site_coord in addresses:
                dist = geodesic(sensor_coord, site_coord).km
                if dist < min_dist:
                    min_dist = dist

            if min_dist > 0.5:
                report.append((sensor_id, round(min_dist, 2)))

    return render_template("index.html", report=report, not_found=not_found)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
