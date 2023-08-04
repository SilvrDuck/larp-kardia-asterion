import asyncio

import websockets
import logging
from definitions import Sound
from playsound import playsound
from threading import Thread
import time

logging.basicConfig(level=logging.DEBUG)

SERVER_URL = "ws://localhost:8000/sound"


loop_queue = asyncio.Queue()
voice_queue = asyncio.Queue()


async def websocket_listener():
    async for websocket in websockets.connect(SERVER_URL):
        try:
            async for message in websocket:
                await process_message(Sound(**message["data"]))
        except websockets.ConnectionClosed:
            logging.error("Connection closed, reconnecting...")

async def process_message(sound: Sound):
    ...

async def loop_player():
    print("starting loop player")
    sound = await loop_queue.get()  # wait initial sound
    print("got initial sound")
    while True:
        playsound(sound)

        try:
            sound = loop_queue.get_nowait()
        except asyncio.QueueEmpty:
            logging.debug("No sound in queue, looping with current sound.")
            pass # keep playing current sound


async def background_loop_player():
    ...


async def voice_player():
    ...

async def instant_play(sound):
    Thread(target=playsound, args=(sound,)).start()

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(loop_player())
        tg.create_task(websocket_listener())




if __name__ == "__main__":
    asyncio.run(main())