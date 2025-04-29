# src/messaging/sender.py

import asyncio
import websockets
import json

class Sender:
    def __init__(self, global_channel_url):
        self.global_channel_url = global_channel_url
        self.websocket = None

    async def connect(self):
        """Connects to the Global Communication Channel."""
        print(f"[Sender] Connecting to Global Channel at {self.global_channel_url}")
        self.websocket = await websockets.connect(self.global_channel_url)
        print(f"[Sender] Connected successfully.")

    async def send(self, message):
        """Sends a message over the WebSocket connection."""
        if self.websocket is None:
            raise RuntimeError("[Sender] WebSocket connection not established. Call connect() first.")

        if hasattr(message, 'content'):
            payload = message.content
        else:
            payload = message  # If it's already a dictionary

        await self.websocket.send(json.dumps(payload))
        print(f"[Sender] Sent message: {payload}")

    async def close(self):
        """Closes the WebSocket connection cleanly."""
        if self.websocket is not None:
            await self.websocket.close()
            print(f"[Sender] Connection closed.")
