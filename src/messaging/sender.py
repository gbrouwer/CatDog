import asyncio
import websockets
import json

class Sender:
    def __init__(self, global_channel_url):
        self.global_channel_url = global_channel_url
        self.websocket = None

    async def connect(self):
        print(f"[Sender] Connecting to Global Channel at {self.global_channel_url}")
        self.websocket = await websockets.connect(self.global_channel_url)
        print("[Sender] Connected.")

    async def send(self, message):
        if self.websocket is None:
            raise RuntimeError("[Sender] Call connect() before sending.")
        payload = message.content if hasattr(message, 'content') else message
        await self.websocket.send(json.dumps(payload))
        print(f"[Sender] Sent: {payload}")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
