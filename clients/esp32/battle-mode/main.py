from umqtt import MQTTClient

import time
import ubinascii
import sys

import machine
from machine import Pin

SERVER_IP = "192.168.17.183"
COLOR_TOPIC = b"COLOR"

# ======================== I/0 ========================

print("Setting up I/O...")

red = Pin(4, Pin.OUT)
green = Pin(18, Pin.OUT)
blue = Pin(19, Pin.OUT)

color_map = {
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "black": (0, 0, 0),
    "white": (1, 1, 1),
    "purple": (1, 0, 1),
    "yellow": (1, 1, 0),
    "cyan": (0, 1, 1),
}

def set_color(r, g, b):
    red.value(r)
    green.value(g)
    blue.value(b)

def set(color):
    set_color(*color_map[color])

def blink_and_set(color, secondary):
    for _ in range(3):
        set(color)
        time.sleep(0.5)
        set("black")
        time.sleep(0.5)
    set(secondary)

# ======================== MQTT ========================

print("Connecting to MQTT...")

mqtt = MQTTClient(
    ubinascii.hexlify(machine.unique_id()),
    SERVER_IP,
    keepalive=60
)

mqtt.connect()

print("Connected!")

def decode_message(message):
    message = message.payload.decode("utf-8")
    try:
        color, mode, secondary = message.split(";")
    except ValueError:
        color, mode = message.split(";")
        secondary = None
    return color, mode, secondary


def receive_callback(topic, msg):
    print("Received message on topic {}: {}".format(topic, msg))
    if topic == COLOR_TOPIC:

        color, mode, secondary = msg.decode("utf-8")        

        if mode == "set":
            set(color)
        elif mode == "blink":
            blink_and_set(color, secondary)
        else:
            print("Unknown mode: {}".format(mode))

mqtt.set_callback(receive_callback)

mqtt.subscribe(COLOR_TOPIC)

# ======================== Main ========================


def main():
    # Asks the server to send the current state of the leds
    mqtt.publish(COLOR_TOPIC, b"__init__", qos=0)
    failure_count = 0
    
    print("Main loop started.")

    while True:
        try:
            # Trigger callbacks for switched switches
            #switches.service_inputs()

            # Trigger led callbacks on new messages
            mqtt.wait_msg()

            failure_count = 0
        except OSError as err:
            print("Warning: MQTT check failed, retry count: {}".format(failure_count))
            failure_count += 1
            if failure_count > 5:
                raise OSError("Too many failed MQTT checks, exiting.") from err


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        print("Exception occured in main loop:")
        sys.print_exception(e)

    finally:
        try:
            mqtt.disconnect()
        finally:
            print("Resetting...")
            machine.reset()
