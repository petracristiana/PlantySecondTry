# Import required libraries
import time
import board
import busio
import digitalio

# SENSOR IMPORTS
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_bmp280
import adafruit_hcsr04

# -------------------------------
# SENSOR INITIALIZATION
# -------------------------------
# 1. SPI & MCP3008 (Analog Sensors)
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D21)
mcp = MCP.MCP3008(spi, cs)
soil_sensor = AnalogIn(mcp, MCP.P0)
light_sensor = AnalogIn(mcp, MCP.P1)

# 2. I2C & BMP280 (Temp/Pressure)
i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
bmp280.sea_level_pressure = 1013.25 

# 3. HC-SR04 (Ultrasonic)
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D25, echo_pin=board.D24)

# -------------------------------
# NORMALIZATION FUNCTIONS
# -------------------------------
def normalize_soil_moisture(raw_value):
    SOIL_DRY = 60000  # <--- CALIBRATE ME! Replace with your dry value
    SOIL_WET = 20000  # <--- CALIBRATE ME! Replace with your wet value
    if SOIL_DRY == SOIL_WET: return 0.0
    percentage = ((SOIL_DRY - raw_value) / (SOIL_DRY - SOIL_WET)) * 100
    return max(0, min(100, round(percentage, 1)))

def normalize_light(raw_value):
    LIGHT_DARK = 29000   # <--- CALIBRATE ME! Raw value when completely covered
    LIGHT_BRIGHT = 60000 # <--- CALIBRATE ME! Raw value under a bright flashlight
    if LIGHT_BRIGHT == LIGHT_DARK: return 0.0
    percentage = ((raw_value - LIGHT_DARK) / (LIGHT_BRIGHT - LIGHT_DARK)) * 100
    return max(0, min(100, round(percentage, 1)))

# -------------------------------
# CONSTANTS (Threshold values)
# -------------------------------
# These values define system conditions using our new 0-100% scales!
SOIL_THRESHOLD = 40      # If soil moisture < 40% → soil is dry
TEMP_THRESHOLD = 25      # If temperature > 25C → too hot
LIGHT_THRESHOLD = 30     # If light < 30% → too dark
WATER_MAX_DISTANCE = 15  # If distance > 15cm → tank is empty! (Change from WATER_MIN)

# -------------------------------
# REAL SENSOR READING FUNCTION
# -------------------------------
# This function pulls live data from the physical sensors
def read_sensors():
    # Read Soil
    soil = normalize_soil_moisture(soil_sensor.value)
    
    # Read Temp
    temp = round(bmp280.temperature, 1)
    
    # Read Light
    light = normalize_light(light_sensor.value)
    
    # Read Ultrasonic
    try:
        water_distance = round(sonar.distance, 1)
    except RuntimeError:
        # Ultrasonic sensors occasionally fail to read an echo
        water_distance = 99.9 # Safe fallback if error
        
    return soil, temp, light, water_distance

# -------------------------------
# MAIN LOGIC FUNCTION
# -------------------------------
# This function acts as the "brain" of the system
# It takes sensor values and decides actions
def greenhouse_logic(soil, temp, light, water_dist):

    # Default states (everything OFF initially)
    pump = False
    window = False
    led = False

    # Pump control logic with safety condition
    # Pump turns ON only if:
    # 1. Soil is dry
    # 2. Water tank is NOT empty (distance to water is LESS than max distance)
    if water_dist < WATER_MAX_DISTANCE and soil < SOIL_THRESHOLD:
        pump = True

    # Temperature control logic
    # If temperature is high → open window for ventilation
    if temp > TEMP_THRESHOLD:
        window = True

    # Light control logic
    # If light is low → turn ON LED
    if light < LIGHT_THRESHOLD:
        led = True

    # Return all actuator states
    return pump, window, led

# -------------------------------
# AI LOGIC FUNCTION
# -------------------------------
# This function analyzes soil trend and predicts drying behavior
def soil_prediction(current, previous):

    # If no previous value exists → cannot predict yet
    if previous is None:
        return "No prediction yet"

    # If current soil value is less than previous → soil is drying
    if current < previous:

        # Calculate how much soil moisture decreased
        change = previous - current

        # Avoid division by zero
        if change > 0:

            # Estimate how many cycles until soil becomes dry
            time_to_dry = current / change

            return f"Soil drying ↓ | Time to dry: {round(time_to_dry,1)} cycles"

    # If soil is not decreasing → stable or increasing
    return "Soil stable ↑"

# -------------------------------
# MAIN LOOP (RUNS FOREVER)
# -------------------------------

previous_soil = None   # Store previous soil value for AI comparison

while True:

    # Step 1: Read sensor values (currently simulated)
    soil, temp, light, water = read_sensors()

    # Step 2: Apply decision logic
    pump, window, led = greenhouse_logic(soil, temp, light, water)

    # Step 3: Run AI prediction
    prediction = soil_prediction(soil, previous_soil)

    # Step 4: Save current soil value for next cycle
    previous_soil = soil

    # Step 5: Print sensor data clearly
    print("\n==============================")
    print("        SENSOR DATA")
    print("==============================")
    print(f"Soil Moisture : {soil}")   # Current soil moisture
    print(f"Temperature   : {temp}")   # Current temperature
    print(f"Light Level   : {light}")  # Current light intensity
    print(f"Water Level   : {water}")  # Current water level

    # Step 6: Print AI prediction
    print("\n--- AI PREDICTION ---")
    print(prediction)

    # Step 7: Print system actions
    print("\n--- SYSTEM ACTIONS ---")
    print(f"Pump   : {'ON ' if pump else 'OFF'}")          # Pump status
    print(f"Window : {'OPEN ' if window else 'CLOSED'}")  # Window status
    print(f"LED    : {'ON ' if led else 'OFF'}")           # LED status

    print("==============================\n")

    # Step 8: Wait 2 seconds before next cycle
    time.sleep(2)
# I will replace the sensor simulation with actual sensor code in the future, but for now this allows us to test the logic and AI prediction effectively.    