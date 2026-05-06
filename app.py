# -------------------------------------------------
# SMART GREENHOUSE FLASK SERVER
# Backend + API + Database
# -------------------------------------------------

# Flask imports
from flask import Flask, jsonify, request

# Import real sensor function from greenhouse.py
from greenhouse import read_sensors

# SQLite database library
import sqlite3


# -------------------------------------------------
# CREATE FLASK APP
# -------------------------------------------------

app = Flask(__name__)


# -------------------------------------------------
# DATABASE SETUP
# -------------------------------------------------
# Create/connect to local SQLite database file

connection = sqlite3.connect(
    "greenhouse.db",
    check_same_thread=False
)

# Create database cursor
cursor = connection.cursor()

# Create sensor_data table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    soil REAL,
    temperature REAL,
    light REAL,
    water_level REAL
)
""")

# Save database changes
connection.commit()


# -------------------------------------------------
# API ROUTE - SENSOR DATA
# -------------------------------------------------
# This route returns LIVE sensor data as JSON
# Example:
# /api/data

@app.route("/api/data")

def get_data():

    # Read real sensor values
    soil, temp, light, water = read_sensors()

    # Save sensor readings into database
    cursor.execute("""
    INSERT INTO sensor_data
    (soil, temperature, light, water_level)

    VALUES (?, ?, ?, ?)
    """, (soil, temp, light, water))

    # Save changes
    connection.commit()

    # Create JSON response
    data = {
        "soil": soil,
        "temperature": temp,
        "light": light,
        "water_level": water
    }

    # Send JSON to dashboard/browser
    return jsonify(data)


# -------------------------------------------------
# API ROUTE - SYSTEM STATUS
# -------------------------------------------------
# This route returns actuator states
# Example:
# /api/status

@app.route("/api/status")

def get_status():

    # Read sensors again
    soil, temp, light, water = read_sensors()

    # Default actuator states
    pump = False
    window = False
    led = False

    # -------------------------------------------------
    # PUMP LOGIC
    # Turn ON if:
    # 1. Soil is dry
    # 2. Water tank is not empty
    # -------------------------------------------------

    if water < 15 and soil < 40:
        pump = True

    # -------------------------------------------------
    # WINDOW LOGIC
    # Open window if temperature is high
    # -------------------------------------------------

    if temp > 25:
        window = True

    # -------------------------------------------------
    # LED LOGIC
    # Turn ON LED if light is low
    # -------------------------------------------------

    if light < 30:
        led = True

    # Create JSON response
    status = {
        "pump": pump,
        "window": window,
        "led": led
    }

    # Send JSON response
    return jsonify(status)


# -------------------------------------------------
# API ROUTE - MANUAL OVERRIDE
# -------------------------------------------------
# This will later receive commands from dashboard
# Example:
# Force pump ON manually

@app.route("/api/override", methods=["POST"])

def manual_override():

    data = request.json

    return jsonify({
        "message": "Override received",
        "data": data
    })


# -------------------------------------------------
# START FLASK SERVER
# -------------------------------------------------

if __name__ == "__main__":

    # Run Flask server
    app.run(

        # Allow other devices on network to connect
        host="0.0.0.0",

        # Server port
        port=5000,

        # Debug mode ON
        debug=True
    )