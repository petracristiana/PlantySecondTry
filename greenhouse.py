# -------------------------------------------------
# SMART GREENHOUSE MAIN BACKEND SYSTEM
# This file handles:
# - Sensor reading
# - AI prediction
# - Decision making
# - Relay control
# -------------------------------------------------

# -------------------------------------------------
# IMPORT REQUIRED LIBRARIES
# -------------------------------------------------

import time                    # Used for delays
import board                   # Raspberry Pi pin references
import busio                   # SPI and I2C communication
import digitalio               # Digital pin control
import RPi.GPIO as GPIO        # GPIO control for relay

# -------------------------------------------------
# SENSOR LIBRARIES
# -------------------------------------------------

# MCP3008 (Analog Sensors)
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# BMP280 (Temperature Sensor)
import adafruit_bmp280

# HC-SR04 (Ultrasonic Sensor)
import adafruit_hcsr04


# -------------------------------------------------
# SENSOR INITIALIZATION
# -------------------------------------------------

# -------------------------------------------------
# 1. SPI SETUP FOR MCP3008
# Used for:
# - Soil moisture sensor
# - Light sensor (LDR)
# -------------------------------------------------

spi = busio.SPI(
    clock=board.SCK,
    MISO=board.MISO,
    MOSI=board.MOSI
)

# Chip Select pin for MCP3008
cs = digitalio.DigitalInOut(board.D21)

# Create MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# Analog channels
soil_sensor = AnalogIn(mcp, MCP.P0)
light_sensor = AnalogIn(mcp, MCP.P1)


# -------------------------------------------------
# 2. I2C SETUP FOR BMP280
# Used for temperature readings
# -------------------------------------------------

i2c = busio.I2C(board.SCL, board.SDA)

bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Sea level pressure for calibration
bmp280.sea_level_pressure = 1013.25


# -------------------------------------------------
# 3. ULTRASONIC SENSOR SETUP
# Used for water tank level detection
# -------------------------------------------------

sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.D25,
    echo_pin=board.D24
)


# -------------------------------------------------
# ACTUATOR SETUP
# -------------------------------------------------
# Relay controls the water pump
# -------------------------------------------------

RELAY_PIN = 17

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set relay pin as output
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Keep pump OFF initially
GPIO.output(RELAY_PIN, GPIO.LOW)


# -------------------------------------------------
# NORMALIZATION FUNCTIONS
# -------------------------------------------------
# Convert raw sensor values into percentages
# -------------------------------------------------

def normalize_soil_moisture(raw_value):

    # Calibration values
    SOIL_DRY = 60000
    SOIL_WET = 20000

    # Prevent division by zero
    if SOIL_DRY == SOIL_WET:
        return 0.0

    # Convert raw value → percentage
    percentage = (
        (SOIL_DRY - raw_value)
        / (SOIL_DRY - SOIL_WET)
    ) * 100

    # Keep values between 0 and 100
    return max(0, min(100, round(percentage, 1)))


def normalize_light(raw_value):

    # Calibration values
    LIGHT_DARK = 29000
    LIGHT_BRIGHT = 60000

    # Prevent division by zero
    if LIGHT_BRIGHT == LIGHT_DARK:
        return 0.0

    # Convert raw value → percentage
    percentage = (
        (raw_value - LIGHT_DARK)
        / (LIGHT_BRIGHT - LIGHT_DARK)
    ) * 100

    # Keep values between 0 and 100
    return max(0, min(100, round(percentage, 1)))


# -------------------------------------------------
# SYSTEM THRESHOLDS
# -------------------------------------------------
# These values control system decisions
# -------------------------------------------------

SOIL_THRESHOLD = 40         # Soil below 40% = dry
TEMP_THRESHOLD = 25         # Above 25°C = hot
LIGHT_THRESHOLD = 30        # Below 30% = dark
WATER_MAX_DISTANCE = 15     # Above 15cm = tank empty


# -------------------------------------------------
# SENSOR READING FUNCTION
# -------------------------------------------------
# Reads all sensors and returns values
# -------------------------------------------------

def read_sensors():

    # Read soil moisture
    soil = normalize_soil_moisture(
        soil_sensor.value
    )

    # Read temperature
    temp = round(
        bmp280.temperature,
        1
    )

    # Read light level
    light = normalize_light(
        light_sensor.value
    )

    # Read ultrasonic distance
    try:
        water_distance = round(
            sonar.distance,
            1
        )

    # Handle sensor read errors
    except RuntimeError:
        water_distance = 99.9

    # Return all values
    return soil, temp, light, water_distance


# -------------------------------------------------
# MAIN GREENHOUSE LOGIC
# -------------------------------------------------
# Makes decisions based on sensor data
# -------------------------------------------------

def greenhouse_logic(
    soil,
    temp,
    light,
    water_dist
):

    # Default actuator states
    pump = False
    window = False
    led = False

    # -------------------------------------------------
    # PUMP LOGIC
    # Turn pump ON if:
    # - Soil is dry
    # - Water tank is not empty
    # -------------------------------------------------

    if (
        water_dist < WATER_MAX_DISTANCE
        and soil < SOIL_THRESHOLD
    ):
        pump = True

    # -------------------------------------------------
    # WINDOW LOGIC
    # Open window if temperature is high
    # -------------------------------------------------

    if temp > TEMP_THRESHOLD:
        window = True

    # -------------------------------------------------
    # LED LOGIC
    # Turn LED ON if environment is dark
    # -------------------------------------------------

    if light < LIGHT_THRESHOLD:
        led = True

    # Return actuator states
    return pump, window, led


# -------------------------------------------------
# AI PREDICTION FUNCTION
# -------------------------------------------------
# Predicts soil drying behavior
# -------------------------------------------------

def soil_prediction(current, previous):

    # No previous data yet
    if previous is None:
        return "No prediction yet"

    # If soil moisture decreased
    if current < previous:

        # Calculate difference
        change = previous - current

        # Prevent division by zero
        if change > 0:

            # Estimate drying time
            time_to_dry = current / change

            return (
                f"Soil drying ↓ | "
                f"Time to dry: "
                f"{round(time_to_dry,1)} cycles"
            )

    # Soil stable or increasing
    return "Soil stable ↑"


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
# Runs system continuously
# -------------------------------------------------

previous_soil = None

try:

    while True:

        # -------------------------------------------------
        # STEP 1: Read Sensors
        # -------------------------------------------------

        soil, temp, light, water = read_sensors()

        # -------------------------------------------------
        # STEP 2: Apply Logic
        # -------------------------------------------------

        pump, window, led = greenhouse_logic(
            soil,
            temp,
            light,
            water
        )

        # -------------------------------------------------
        # STEP 3: Relay Control
        # Physically control water pump
        # -------------------------------------------------

        if pump:
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        else:
            GPIO.output(RELAY_PIN, GPIO.LOW)

        # -------------------------------------------------
        # STEP 4: AI Prediction
        # -------------------------------------------------

        prediction = soil_prediction(
            soil,
            previous_soil
        )

        # Save current value for next comparison
        previous_soil = soil

        # -------------------------------------------------
        # STEP 5: Print Sensor Data
        # -------------------------------------------------

        print("\n==============================")
        print("        SENSOR DATA")
        print("==============================")

        print(f"Soil Moisture : {soil}")
        print(f"Temperature   : {temp}")
        print(f"Light Level   : {light}")
        print(f"Water Level   : {water}")

        # -------------------------------------------------
        # STEP 6: Print AI Prediction
        # -------------------------------------------------

        print("\n--- AI PREDICTION ---")
        print(prediction)

        # -------------------------------------------------
        # STEP 7: Print System Actions
        # -------------------------------------------------

        print("\n--- SYSTEM ACTIONS ---")

        print(f"Pump   : {'ON ' if pump else 'OFF'}")
        print(f"Window : {'OPEN ' if window else 'CLOSED'}")
        print(f"LED    : {'ON ' if led else 'OFF'}")

        print("==============================\n")

        # Wait 2 seconds
        time.sleep(2)

# Stop program safely
except KeyboardInterrupt:

    print("\nSystem stopped.")

# Clean GPIO pins before exit
finally:

    GPIO.cleanup()