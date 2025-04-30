print(f"[DEBUG] gcc.py running from: {__file__}")
import websockets
print(f"[DEBUG] Running websockets version: {websockets.__version__}")
import asyncio

connected_clients = set()

async def gcc_handler(websocket):
    print(f"[GCC] New client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"[GCC] Message received: {message}")
            await broadcast(message)
    except websockets.ConnectionClosed:
        print(f"[GCC] Client disconnected: {websocket.remote_address}")
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
    print("[GCC] Starting Global Communication Channel on ws://0.0.0.0:9000/global")
    print(f"[DEBUG] Serving with: {gcc_handler}")
    print(f"[DEBUG] Args: {gcc_handler.__code__.co_varnames[:gcc_handler.__code__.co_argcount]}")
    async with websockets.serve(gcc_handler, "0.0.0.0", 9000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
