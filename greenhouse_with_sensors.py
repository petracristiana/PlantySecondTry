import paho.mqtt.client as mqtt
import json

import time
import board
import busio
import digitalio

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_bmp280
import adafruit_hcsr04

# SPI setup for analog sensors
spi = busio.SPI(
    clock=board.SCK,
    MISO=board.MISO,
    MOSI=board.MOSI
)

cs = digitalio.DigitalInOut(board.D21)

mcp = MCP.MCP3008(spi, cs)

soil_sensor = AnalogIn(mcp, MCP.P0)
light_sensor = AnalogIn(mcp, MCP.P1)

# I2C setup for BMP280
i2c = busio.I2C(
    board.SCL,
    board.SDA
)

bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

bmp280.sea_level_pressure = 1013.25

# Ultrasonic sensor setup
sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.D25,
    echo_pin=board.D24
)

# MQTT settings
broker = "broker.hivemq.com"
port = 1883
topic = "plant/data"

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1
)

client.connect(
    broker,
    port,
    60
)

# MQTT connection check
if client.is_connected():

    print("✅ MQTT BROKER CONNECTED")

else:

    print("❌ MQTT NOT CONNECTED")

# Convert soil value to percentage
def normalize_soil_moisture(raw_value):

    SOIL_DRY = 28000
    SOIL_WET = 52000

    if SOIL_DRY == SOIL_WET:
        return 0.0

    percentage = (
        (SOIL_DRY - raw_value)
        / (SOIL_DRY - SOIL_WET)
    ) * 100

    return max(
        0,
        min(100, round(percentage, 1))
    )

# Convert light value to percentage
def normalize_light(raw_value):

    LIGHT_DARK = 5000
    LIGHT_BRIGHT = 60000

    if LIGHT_BRIGHT == LIGHT_DARK:
        return 0.0

    percentage = (
        (raw_value - LIGHT_DARK)
        / (LIGHT_BRIGHT - LIGHT_DARK)
    ) * 100

    return max(
        0,
        min(100, round(percentage, 1))
    )

# Threshold values
SOIL_THRESHOLD = 40
TEMP_THRESHOLD = 25
LIGHT_THRESHOLD = 30
WATER_MAX_DISTANCE = 15

# Read all sensor values
def read_sensors():

    soil = normalize_soil_moisture(
        soil_sensor.value
    )

    temp = round(
        bmp280.temperature,
        1
    )

    light = normalize_light(
        light_sensor.value
    )

    try:

        water_distance = round(
            sonar.distance,
            1
        )

    except RuntimeError:

        water_distance = 99.9

    return soil, temp, light, water_distance

# Greenhouse automation logic
def greenhouse_logic(
    soil,
    temp,
    light,
    water_dist
):

    pump = False
    window = False
    led = False

    # Turn ON pump if soil is dry
    if (
        water_dist < WATER_MAX_DISTANCE
        and soil < SOIL_THRESHOLD
    ):
        pump = True

    # Open window if temperature is high
    if temp > TEMP_THRESHOLD:
        window = True

    # Turn ON LED if light is low
    if light < LIGHT_THRESHOLD:
        led = True

    return pump, window, led

# Predict soil drying trend
def soil_prediction(
    current,
    previous
):

    if previous is None:
        return "No prediction yet"

    if current < previous:

        change = previous - current

        if change > 0:

            time_to_dry = current / change

            return (
                f"Soil drying ↓ | "
                f"Time to dry: "
                f"{round(time_to_dry,1)} cycles"
            )

    return "Soil stable ↑"

# Store previous soil value
previous_soil = None

# Main program loop
while True:

    # Read sensor data
    soil, temp, light, water = read_sensors()

    # Create MQTT payload
    payload = {

        "soil": soil,
        "temperature": temp,
        "light": light,
        "water": water

    }

    # Send data to MQTT broker
    try:

        result = client.publish(
            topic,
            json.dumps(payload)
        )

        status = result[0]

        if status == 0:

            print("📡 MQTT DATA SENT SUCCESSFULLY")

        else:

            print("❌ MQTT SEND FAILED")

    except Exception as e:

        print(f"❌ MQTT ERROR: {e}")

    # Apply greenhouse logic
    pump, window, led = greenhouse_logic(
        soil,
        temp,
        light,
        water
    )

    # Run AI prediction
    prediction = soil_prediction(
        soil,
        previous_soil
    )

    previous_soil = soil

    # Print sensor data
    print("\n================================")
    print("        SENSOR DATA")
    print("================================")

    print(f"Soil Moisture : {soil}")
    print(f"Temperature   : {temp}")
    print(f"Light Level   : {light}")
    print(f"Water Level   : {water}")

    print("\n--- AI PREDICTION ---")
    print(prediction)

    print("\n--- SYSTEM ACTIONS ---")

    print(
        f"Pump   : "
        f"{'ON' if pump else 'OFF'}"
    )

    print(
        f"Window : "
        f"{'OPEN' if window else 'CLOSED'}"
    )

    print(
        f"LED    : "
        f"{'ON' if led else 'OFF'}"
    )

    print("================================\n")

    # Wait before next cycle
    time.sleep(2)