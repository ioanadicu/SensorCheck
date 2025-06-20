from flask import Flask, render_template, request
import googlemaps
from config import GOOGLE_MAPS_API_KEY
from geopy.distance import geodesic
import csv
import io

from flask import send_file
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import os

from config import AXIFLEET_API_KEY
import requests
import datetime

app = Flask(__name__)

# data cea mai recenta, denumirea locatiei 

@app.route("/", methods=["GET", "POST"])
def index():
    report = []
    not_found = []

    if request.method == "POST":
        use_axifleet = request.form.get("use_axifleet") == "on"

        # Procesare adrese (din fișier TXT)
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

        # Procesare senzori: fie din fișier, fie din API
        sensors = []
        if use_axifleet:
            from get_sensors_from_axifleet import get_sensor_data_from_axifleet
            sensors = get_sensor_data_from_axifleet()
            print(f"[DEBUG] Am primit {len(sensors)} senzori din API")
        else:
            sensor_file = request.files["sensors"]
            reader = csv.DictReader(io.StringIO(sensor_file.read().decode('utf-8')))
            for row in reader:
                sensors.append({
                    "SensorID": row["SensorID"],
                    "Latitude": float(row["Latitude"]),
                    "Longitude": float(row["Longitude"])
                })

        # Calcul distanțe
        for sensor in sensors:
            sensor_id = sensor["SensorID"]
            sensor_coord = (sensor["Latitude"], sensor["Longitude"])

            min_dist = float("inf")
            closest_address = "Adresă necunoscută"

            for site_address, site_coord in addresses:
                dist = geodesic(sensor_coord, site_coord).km
                if dist < min_dist:
                    min_dist = dist
                    closest_address = site_address

            if min_dist > 0.5:
                report.append({
                    "SensorID": sensor_id,
                    "Distance": round(min_dist, 2),
                    "Address": closest_address
                })

    return render_template("index.html", report=report, not_found=not_found)

@app.route("/download", methods=["POST"])
def download_pdf():
    report_data = request.form.get("report", "").replace("\\n", "\n")
    not_found_data = request.form.get("not_found", "").replace("\\n", "\n")

    # Înregistrăm un font care suportă diacritice
    font_path = "static/fonts/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        font_name = "DejaVuSans"
    else:
        font_name = "Helvetica"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        c = canvas.Canvas(tmp.name, pagesize=A4)
        width, height = A4
        y = height - 50

        c.setFont(font_name, 14)
        c.drawString(50, y, "Raport senzori – distanță minimă față de șantiere")
        y -= 30

        c.setFont(font_name, 12)
        c.drawString(50, y, "Senzori aflați la peste 0.5 km de orice șantier:")
        y -= 20

        for line in report_data.splitlines():
            if y < 50:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 50
            c.drawString(60, y, line.strip())
            y -= 20

        y -= 20
        c.drawString(50, y, "Adrese negăsite (erori geocodare):")
        y -= 20

        for line in not_found_data.splitlines():
            if y < 50:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 50
            c.drawString(60, y, line.strip())
            y -= 20

        c.save()
        return send_file(tmp.name, as_attachment=True, download_name="raport_senzori.pdf")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
