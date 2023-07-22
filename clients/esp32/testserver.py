from fastapi import FastAPI
from fastapi.websockets import WebSocket
import asyncio
import json

app = FastAPI()

q = asyncio.Queue()

async def get_data_loop(ws):
    while True:
        data = await ws.receive_text()
        data = json.loads(data)
        print(f"Received: {data}")
        await q.put(data["switch"])


async def send_data_loop(ws):

    while True:
        state = await q.get()
        print(f"Sending: {state}")
        await ws.send_text(json.dumps({"led": state}))



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await asyncio.gather(get_data_loop(websocket), send_data_loop(websocket))


@app.get("/test")
async def test():
    return {"message": "Hello World"}