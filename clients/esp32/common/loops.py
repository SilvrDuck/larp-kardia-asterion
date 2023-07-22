import uasyncio
import config
from wifi import connect
from async_websocket import AsyncWebsocketClient
import json
import sys

client = AsyncWebsocketClient()


async def sender_loop(update_method):
    while await client.open():
        try:
            message = await update_method()
            message = json.dumps(message)
        except Exception as e:
            print("Error in update_method:")
            sys.print_exception(e)
            continue

        await client.send(message)

async def receiver_loop(data_callback):
    while await client.open():
        data = await client.recv()

        if data is not None:
            data = json.loads(data)
            try:
                await data_callback(data)
            except Exception as e:
                print("Error in data_callback:")
                sys.print_exception(e)
        
        await uasyncio.sleep_ms(50)

async def check_connection_loop():
    while True:
        #connect()
        await uasyncio.sleep(4)


async def wait_for_handshake(target_route: str):
    while True:
        try:
            await client.handshake(config.SERVER_URL + target_route)
            print("Handshake successful")
            break
        except OSError:
            print("Handshake failed. Retrying...")
            await uasyncio.sleep(1)


async def main(
    update_method,
    data_callback,
    target_route,
):
    await wait_for_handshake(target_route)
    await uasyncio.gather(
        sender_loop(update_method),
        receiver_loop(data_callback),
        #check_connection_loop(),
    )


def persistent_main(
    update_method,
    data_callback,
    target_route,
):
    while True:
        try:
            print("TODO: need to handle wifi disconnects")
                  
            print("Starting")
            uasyncio.run(main(
                update_method,
                data_callback,
                target_route,
            ))
            print("Main loop exited. Restarting...")
        except Exception as e:
            print("Main loop crashed. Restarting...")
            sys.print_exception(e)
