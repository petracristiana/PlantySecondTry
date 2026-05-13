# ============================================
# SMART GREENHOUSE RGB STATUS SYSTEM
# ============================================

import RPi.GPIO as GPIO
import time

# ============================================
# GPIO MODE
# ============================================
# Using BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# ============================================
# RGB LED GPIO PINS
# ============================================
# Based on your wiring

RED_PIN = 22
GREEN_PIN = 27
BLUE_PIN = 17

# ============================================
# SET RGB PINS AS OUTPUT
# ============================================

GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

# ============================================
# FUNCTION TO CONTROL RGB LED
# ============================================
# True = ON
# False = OFF

def set_rgb(red, green, blue):

    GPIO.output(RED_PIN, red)
    GPIO.output(GREEN_PIN, green)
    GPIO.output(BLUE_PIN, blue)

# ============================================
# MAIN LOOP
# ============================================

try:

    while True:

        # ====================================
        # FAKE SENSOR VALUES (FOR TESTING)
        # ====================================
        # Change these values manually to test

        soil = 35
        temperature = 30
        water_level = 10

        # ====================================
        # DANGER CONDITION → RED
        # ====================================
        # Example:
        # Very hot OR water tank empty

        if temperature > 30 or water_level < 15:

            print("PLANT IN DANGER → RED 🔴")

            # RED
            set_rgb(True, False, False)

        # ====================================
        # WARNING CONDITION → ORANGE
        # ====================================
        # Example:
        # Soil becoming dry

        elif soil < 40:

            print("WARNING → ORANGE 🟠")

            # ORANGE = RED + GREEN
            set_rgb(True, True, False)

        # ====================================
        # HEALTHY CONDITION → GREEN
        # ====================================

        else:

            print("PLANT HEALTHY → GREEN 🟢")

            # GREEN
            set_rgb(False, True, False)

        # Wait before next cycle
        time.sleep(3)

# ============================================
# STOP PROGRAM SAFELY
# ============================================

except KeyboardInterrupt:

    print("Program Stopped")

finally:

    GPIO.cleanup()