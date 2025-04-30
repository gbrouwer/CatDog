# gcc.py

from log import log, log_error
import websockets
import asyncio

connected_clients = set()

async def gcc_handler(websocket):
    log("GCC", f"New client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            log("GCC", f"Message received: {message}")
            await broadcast(message)
    except websockets.ConnectionClosed:
        log("GCC", f"Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    dead_clients = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.ConnectionClosed:
            dead_clients.add(client)
    connected_clients.difference_update(dead_clients)

async def main():
    log("GCC", "Starting Global Communication Channel on ws://0.0.0.0:9000/global")
    log("GCC", f"Serving with: {gcc_handler}")
    log("GCC", f"Args: {gcc_handler.__code__.co_varnames[:gcc_handler.__code__.co_argcount]}")
    async with websockets.serve(gcc_handler, "0.0.0.0", 9000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
