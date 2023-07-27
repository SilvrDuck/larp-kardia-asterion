from fastapi import FastAPI
from paho.mqtt.client import Client as MQTTClient
from collections import defaultdict
app = FastAPI()
mqtt = MQTTClient()
mqtt.connect("localhost", 1883, 60)

state = defaultdict(int)

def on_message(client, userdata, message):

    message = message.payload.decode("utf-8")

    if message == "__init__":
        print("recieved init")
        for key, value in state.items():
            mqtt.publish("led", key + str(int(value)))
        return

    print("Received ", message)

    # switch
    state[message] = not state[message]

    to_up = turnoffiffull()
    #to_up = []
    to_up.append(message)

    for message in to_up:
        print("Sending ", message + str(int(state[message])))
        mqtt.publish("led", message + str(int(state[message])))

def turnoffiffull():
    to_update = []
    for color in ["EF", "WF", "NF", "SF"]:
        keys_for_col = [key for key in state.keys() if key.startswith(color)]
        bk = False
        print("checking ", keys_for_col, state)
        for k in keys_for_col:
            if state[k] == 0:
                bk = True

        if bk:
            continue
        # if all are 1
        print("turning off ", keys_for_col)
        for k in keys_for_col:
            state[k] = 0
            to_update.append(k)
    return to_update
            

mqtt.on_message = on_message
mqtt.subscribe("switch")
mqtt.loop_start()