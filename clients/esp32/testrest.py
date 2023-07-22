from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig

app = FastAPI()

mqtt_config = MQTTConfig()

mqtt = FastMQTT(
    config=mqtt_config
)

mqtt.init_app(app)

@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("test")

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: " + topic + payload.decode())
    mqtt.publish("fromfast", payload)



