import paho.mqtt.client as mqtt
import json

import board
import digitalio
import time

# RGB LED pins
red_led = digitalio.DigitalInOut(board.D5)
green_led = digitalio.DigitalInOut(board.D6)
blue_led = digitalio.DigitalInOut(board.D13)

red_led.direction = digitalio.Direction.OUTPUT
green_led.direction = digitalio.Direction.OUTPUT
blue_led.direction = digitalio.Direction.OUTPUT

# Relay pin
relay = digitalio.DigitalInOut(board.D23)
relay.direction = digitalio.Direction.OUTPUT

# Stepper motor pins
motor_pins = [
    digitalio.DigitalInOut(board.D17),
    digitalio.DigitalInOut(board.D18),
    digitalio.DigitalInOut(board.D27),
    digitalio.DigitalInOut(board.D22)
]

for pin in motor_pins:
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = False

# Stepper motor sequence
sequence = [
    [True,  False, False, False],
    [True,  True,  False, False],
    [False, True,  False, False],
    [False, True,  True,  False],
    [False, False, True,  False],
    [False, False, True,  True ],
    [False, False, False, True ],
    [True,  False, False, True ]
]

# Turn OFF all RGB colors
def clear_lights():

    red_led.value = False
    green_led.value = False
    blue_led.value = False

# Red status for dry soil
def red_status():

    clear_lights()
    red_led.value = True

# Yellow status for warning
def yellow_status():

    clear_lights()
    red_led.value = True
    green_led.value = True

# Green status for healthy plant
def green_status():

    clear_lights()
    green_led.value = True

# Rotate stepper motor
def rotate(steps, direction=1, delay=0.001):

    for i in range(steps):

        if direction == 1:
            seq_index = i % 8
        else:
            seq_index = 7 - (i % 8)

        row = sequence[seq_index]

        motor_pins[0].value = row[0]
        motor_pins[1].value = row[1]
        motor_pins[2].value = row[2]
        motor_pins[3].value = row[3]

        time.sleep(delay)

# MQTT settings
broker = "broker.hivemq.com"
port = 1883
topic = "plant/data"

# Sensor values
soil = 0
temp = 0

# Receive MQTT data
def on_message(client, userdata, msg):

    global soil, temp

    data = json.loads(msg.payload.decode())

    soil = data["soil"]
    temp = data["temperature"]

    print("MQTT DATA RECEIVED")
    print(data)

# MQTT client setup
client = mqtt.Client()

client.on_message = on_message

client.connect(
    broker,
    port,
    60
)

client.subscribe(topic)

client.loop_start()

print("MQTT Connected")

# Main greenhouse loop
try:

    print("\n--- SMART GREENHOUSE ACTIVE ---\n")

    while True:

        print(f"Soil Moisture: {soil}")
        print(f"Temperature: {temp}")

        # Dry soil condition
        if soil < 30:

            print("🔴 Plant in danger")

            red_status()

            relay.value = True

        # Medium soil condition
        elif soil < 50:

            print("🟡 Plant needs attention")

            yellow_status()

            relay.value = False

        # Healthy soil condition
        else:

            print("🟢 Plant healthy")

            green_status()

            relay.value = False

        # High temperature condition
        if temp > 25:

            print("🌡️ High temperature → Opening roof")

            rotate(
                steps=100,
                direction=1,
                delay=0.001
            )

        else:

            print("🌡️ Temperature normal")

        print("----------------------------\n")

        time.sleep(3)

# Stop system safely
except KeyboardInterrupt:

    print("\nSystem stopped cleanly.")

finally:

    clear_lights()

    relay.value = False

    for pin in motor_pins:
        pin.value = False

    print("All systems safely turned OFF.")