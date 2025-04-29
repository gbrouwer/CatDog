# global_channel.py
import asyncio
import websockets
import json

# List of all connected WebSocket clients
connected_clients = set()

async def handler(websocket, path):
    # Register new client
    print(f"[GCC] New client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"[GCC] Message received: {message}")
            # Broadcast incoming message to all clients
            await broadcast(message)
    except websockets.ConnectionClosed:
        print(f"[GCC] Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    # Send the message to all connected clients
    dead_clients = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.ConnectionClosed:
            dead_clients.add(client)
    
    # Remove any dead clients
    for client in dead_clients:
        connected_clients.remove(client)

async def main():
    print("[GCC] Starting Global Communication Channel on ws://0.0.0.0:9000/global")
    async with websockets.serve(handler, "0.0.0.0", 9000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
