import time
import board
import busio
import digitalio

# ---------------------------------------------------------
# 1. SENSOR IMPORTS
# ---------------------------------------------------------
# MCP3008 (Analog-to-Digital Converter)
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# BMP280 (Temperature and Pressure)
import adafruit_bmp280

# HC-SR04 (Ultrasonic Water Level)
import adafruit_hcsr04

# ---------------------------------------------------------
# 2. SENSOR INITIALIZATION
# ---------------------------------------------------------

# A. SPI Bus & MCP3008 Setup
# The Raspberry Pi uses SCK (Pin 23), MISO (Pin 21), and MOSI (Pin 19)
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Chip Select (CS) is on GPIO 21 (Pin 40)
cs = digitalio.DigitalInOut(board.D21)
mcp = MCP.MCP3008(spi, cs)

# Define our analog channels
soil_sensor = AnalogIn(mcp, MCP.P0) # CH0
light_sensor = AnalogIn(mcp, MCP.P1) # CH1

# B. I2C Bus & BMP280 Setup
# The Pi uses SCL (Pin 5) and SDA (Pin 3)
i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
# Set local sea level pressure for accurate altitude calculation (optional)
bmp280.sea_level_pressure = 1013.25 

# C. HC-SR04 Ultrasonic Setup
# Trig is GPIO 25 (Pin 22), Echo is GPIO 24 (Pin 18)
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D25, echo_pin=board.D24)

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS (NORMALIZATION)
# ---------------------------------------------------------

def normalize_soil_moisture(raw_value):
    """
    Converts the raw 16-bit analog value (0 - 65535) from the soil sensor 
    into a percentage (0% - 100%).
    
    IMPORTANT: You must calibrate these MIN and MAX values!
    - SOIL_DRY: The raw value when the sensor is completely dry (in the air).
    - SOIL_WET: The raw value when the sensor is completely submerged in water.
    
    Note: Capacitive sensors usually output a HIGH value when dry, and a LOW value when wet.
    """
    SOIL_DRY = 60000  # <--- CALIBRATE ME! Replace with your dry value
    SOIL_WET = 20000  # <--- CALIBRATE ME! Replace with your wet value
    
    # Calculate percentage using a linear mapping formula
    # If raw_value is exactly SOIL_DRY, it evaluates to 0%
    # If raw_value is exactly SOIL_WET, it evaluates to 100%
    percentage = ((SOIL_DRY - raw_value) / (SOIL_DRY - SOIL_WET)) * 100
    
    # Clamp the percentage between 0 and 100
    percentage = max(0, min(100, percentage))
    return round(percentage, 1)

def normalize_light(raw_value):
    """
    Converts the raw LDR value into a 0-100% brightness scale.
    Because of our voltage divider, higher light = higher voltage.
    """
    LIGHT_DARK = 29000   # <--- CALIBRATE ME! Raw value when completely covered
    LIGHT_BRIGHT = 60000 # <--- CALIBRATE ME! Raw value under a bright flashlight
    
    # Calculate percentage using a linear mapping formula
    # Prevent division by zero if values are the same
    if LIGHT_BRIGHT == LIGHT_DARK:
        return 0.0
        
    percentage = ((raw_value - LIGHT_DARK) / (LIGHT_BRIGHT - LIGHT_DARK)) * 100
    
    # Clamp the percentage between 0 and 100
    percentage = max(0, min(100, percentage))
    return round(percentage, 1)

# ---------------------------------------------------------
# 4. MAIN LOOP (THE "CREATE" PHASE OF THE IoT LOOP)
# ---------------------------------------------------------

print("Starting Smart Greenhouse Sensor Collection...")
print("Press Ctrl+C to stop.")

try:
    while True:
        print("-" * 40)
        
        # --- 1. Read and Normalize Analog Sensors (MCP3008) ---
        raw_soil = soil_sensor.value
        soil_percent = normalize_soil_moisture(raw_soil)
        
        raw_light = light_sensor.value
        light_percent = normalize_light(raw_light)
        
        print(f"Soil Moisture: {soil_percent}%  (Raw: {raw_soil})")
        print(f"Light Level:   {light_percent}%  (Raw: {raw_light})")
        
        # --- 2. Read I2C Sensor (BMP280) ---
        temp_c = bmp280.temperature
        pressure = bmp280.pressure
        print(f"Temperature:   {temp_c:.1f} °C")
        print(f"Pressure:      {pressure:.1f} hPa")
        
        # --- 3. Read Digital Sensor (HC-SR04) ---
        try:
            # The distance is returned in centimeters
            distance_cm = sonar.distance
            print(f"Water Tank Level (Distance): {distance_cm:.1f} cm")
        except RuntimeError:
            # Ultrasonic sensors occasionally fail to read an echo. We catch the error to prevent crashes.
            print("Water Tank Level: [Read Error - Retrying next loop]")
            
        # Wait 2 seconds before collecting data again
        time.sleep(2)

except KeyboardInterrupt:
    print("\nSensor script stopped by user.")
finally:
    # Always turn off the sonar to clean up GPIO state
    sonar.deinit()
