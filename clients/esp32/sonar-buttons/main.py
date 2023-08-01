from umqtt import MQTTClient

import time
import ubinascii
import sys
from config import global_config, SERVER_IP, SWITCH_TOPIC, LED_TOPIC, CONTROL_PANEL

import json

import machine
from machine import Pin
from inputs import Manager, Digital


# Each esp32 uses a different config
config = global_config[CONTROL_PANEL]

# ======================== MQTT ========================

print("Connecting to MQTT...")

mqtt = MQTTClient(ubinascii.hexlify(machine.unique_id()), SERVER_IP, keepalive=60)

mqtt.connect()

print("Connected!")


def decode_msg(msg):
    """Message format: {code}{value},
    where code is a 4 character string and value is 0 or 1.

    See config.py for more details.
    """
    message = msg.decode("utf-8")
    print("Decoding message: {}".format(message))
    return message[:4], int(message[4:])


def receive_callback(topic, msg):
    print("Received message on topic {}: {}".format(topic, msg))
    if topic == LED_TOPIC:
        led, value = decode_msg(msg)
        print("Setting led {} to {}".format(led, value))

        try:
            leds[led].value(value)
        except KeyError:
            pass  # led meant for another board


mqtt.set_callback(receive_callback)

mqtt.subscribe(LED_TOPIC)


# ======================== I/0 ========================

print("Setting up I/O...")

leds = {item["code"]: Pin(item["led"], Pin.OUT) for item in config}


def switch_led(led):
    led.value(not led.value())


def switch_callback(input_name):
    switch_led(leds[input_name])
    print("Sending switch {} to server".format(input_name))
    mqtt.publish(SWITCH_TOPIC, input_name.encode("utf-8"), qos=0)
    print("Sent!")


switches = Manager(
    [
        Digital(
            "{}: {}".format(item["switch"], item["code"]),
            switch_func=switch_callback,
            stable_read_count=4,
        )
        for item in config
    ],
    poll_freq=100,
)


# ======================== Main ========================


def main():
    # Asks the server to send the current state of the leds
    mqtt.publish(SWITCH_TOPIC, b"__init__", qos=0)
    failure_count = 0

    print("Main loop started.")

    while True:
        try:
            # Trigger callbacks for switched switches
            # switches.service_inputs()

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
