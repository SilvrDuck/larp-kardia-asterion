from umqtt import MQTTClient

import time
import ubinascii
import sys
from config import global_config, SERVER_IP, SWITCH_TOPIC, LED_TOPIC

import json

import machine
from machine import Pin
from inputs import Manager, Digital


# Each esp32 uses a different config
config = global_config["pannel_a"]

def system_blink(count=1):
    """Used for startup diagnostics"""
    for _ in range(count):
        diagnostic_led.value(1)
        time.sleep_ms(100)
        diagnostic_led.value(0)
        time.sleep_ms(100)

# ======================== I/0 ========================

leds = {
    item["code"]: Pin(item["led"], Pin.OUT)
    for item in config
}

diagnostic_led = leds[list(leds.keys())[0]]

print("Startng set up...")

def switch_led(led):
    led.value(not led.value())

def switch_callback(input_name):
    switch_led(leds[input_name])
    mqtt.publish(SWITCH_TOPIC, input_name.encode("utf-8"), qos=1)



switches = Manager(
    [
        Digital(
            "{}: {}".format(item["switch"], item["code"]), 
            switch_func=switch_callback,
        )
        for item in config
    ],
    timer_num=None,  # Use manual polling
)


# ======================== MQTT ========================

print("Connecting to MQTT...")

mqtt = MQTTClient(
    ubinascii.hexlify(machine.unique_id()),
    SERVER_IP,
    keepalive=60
)

mqtt.connect()

print("Connected!")

def decode_msg(msg):
    """Message format: {code}{value},
    where code is a 4 character string and value is 0 or 1.

    See config.py for more details.
    """
    message = msg.decode("utf-8")
    return message[:4], int(message[4:])

def receive_callback(topic, msg):
    print("Received message on topic {}:".format(topic))
    if topic == LED_TOPIC:
        led, value = decode_msg(msg)
        leds[led].value(value)

mqtt.set_callback(receive_callback)

mqtt.subscribe(LED_TOPIC)


# ======================== Main ========================


def main():
    # Asks the server to send the current state of the leds
    mqtt.publish(SWITCH_TOPIC, b"__init__", qos=1)
    failure_count = 0
    
    print("Main loop started.")

    while True:
        try:
            # Trigger callbacks for switched switches
            switches.service_inputs()

            # Trigger led callbacks on new messages
            mqtt.check_msg()

            failure_count = 0
        except OSError as err:
            print("Warning: MQTT check failed, retry count: {}".format(failure_count))
            failure_count += 1
            if failure_count > 5:
                raise OSError("Too many failed MQTT checks, exiting.") from err

        time.sleep_ms(10)


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
