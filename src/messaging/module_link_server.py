import asyncio
import websockets
import json

class ModuleLinkServer:
    def __init__(self, host="0.0.0.0", port=9100):
        self.clients = set()
        self.host = host
        self.port = port

    async def handler(self, websocket):
        print(f"[ModuleLinkServer] Client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            print(f"[ModuleLinkServer] Client disconnected: {websocket.remote_address}")
            self.clients.remove(websocket)

    async def start(self):
        print(f"[ModuleLinkServer] Starting on ws://{self.host}:{self.port}")
        self.server = await websockets.serve(
            self.handler,
            self.host,
            self.port
        )

    async def broadcast(self, payload: dict):
        """Send JSON message to all connected clients."""
        message = json.dumps(payload)
        dead = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.ConnectionClosed:
                dead.add(client)
        self.clients -= dead

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        print("[ModuleLinkServer] Server stopped.")
