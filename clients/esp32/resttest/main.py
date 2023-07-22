from umqtt import MQTTClient

from machine import Pin
import time
from switch import Switch

switch = Switch(Pin(18, Pin.IN, Pin.PULL_UP), check_period=10)
led = Pin(4, Pin.OUT)

def blink():
    led.value(1)
    time.sleep(0.5)
    led.value(0)
    time.sleep(0.5)


client = MQTTClient("esp32", "192.168.1.40", keepalive=60)

print("Connecting to MQTT broker...")
while True:
    try:
        client.connect()
    except Exception:
        time.sleep(1)
        continue
    break

print("Connected!")
blink()
blink()

client.set_callback(
    lambda topic, msg: led.value(int(msg.decode()))
)

client.subscribe("fromfast")

try:
    while True:
        if switch.new_value_available:
            print("Switch value changed")
            new_val = switch.value()
            print("New value: " + str(new_val))
            client.publish("test", str(new_val).encode(), qos=1)
        message = client.check_msg()
        time.sleep_ms(10)
finally:
    client.disconnect()