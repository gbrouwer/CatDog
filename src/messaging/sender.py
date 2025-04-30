import asyncio
import websockets
import json
from log import log, log_error

class Sender:
    def __init__(self, global_channel_url, tag="Sender"):
        self.global_channel_url = global_channel_url
        self.websocket = None
        self.tag = tag

    async def connect(self):
        log(self.tag, f"Connecting to Global Channel at {self.global_channel_url}")
        self.websocket = await websockets.connect(self.global_channel_url)
        log(self.tag, "Connected.")

    async def send(self, message):
        if self.websocket is None:
            raise RuntimeError(f"[{self.tag}] Call connect() before sending.")
        payload = message.content if hasattr(message, 'content') else message
        await self.websocket.send(json.dumps(payload))
        log(self.tag, f"Sent: {payload}")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            log(self.tag, "Connection closed.")

