# Import required libraries
import time        # Used to create delay between loops
import random      # Used to generate fake sensor values (Day 1 testing)

# -------------------------------
# CONSTANTS (Threshold values)
# -------------------------------
# These values define system conditions
SOIL_THRESHOLD = 40      # If soil moisture < 40 → soil is dry
TEMP_THRESHOLD = 25      # If temperature > 25 → too hot
LIGHT_THRESHOLD = 300    # If light < 300 → too dark
WATER_MIN = 20           # Minimum water level required to allow pump

# -------------------------------
# SENSOR SIMULATION FUNCTION
# -------------------------------
# This function simulates real sensor readings using random values
# will be replaced with actual sensor code in the future
def read_sensors():
    soil = random.randint(20, 60)     # Simulated soil moisture value
    temp = random.randint(15, 35)     # Simulated temperature value
    light = random.randint(100, 500)  # Simulated light intensity
    water = random.randint(10, 100)   # Simulated water level
    return soil, temp, light, water   # Return all values together

# -------------------------------
# MAIN LOGIC FUNCTION
# -------------------------------
# This function acts as the "brain" of the system
# It takes sensor values and decides actions
def greenhouse_logic(soil, temp, light, water):

    # Default states (everything OFF initially)
    pump = False
    window = False
    led = False

    # Pump control logic with safety condition
    # Pump turns ON only if:
    # 1. Soil is dry
    # 2. Water level is sufficient
    if water >= WATER_MIN and soil < SOIL_THRESHOLD:
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