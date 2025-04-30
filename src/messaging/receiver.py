import asyncio
import websockets
import json

class Receiver:
    def __init__(self, global_channel_url, on_message_callback, module=None):
        self.global_channel_url = global_channel_url
        self.on_message_callback = on_message_callback
        self.websocket = None
        self.module = module

    async def run(self):
        print(f"[Receiver] Connecting to Global Channel at {self.global_channel_url}")
        while True:
            try:
                self.websocket = await websockets.connect(self.global_channel_url)
                print("[Receiver] Connected.")
                if self.module:
                    self.module.connection_status = ConnectionStatus.CONNECTED

                async for message in self.websocket:
                    data = json.loads(message)
                    await self.on_message_callback(data)

            except Exception as e:
                print(f"[Receiver] Connection error: {e}")
                if self.module:
                    self.module.connection_status = ConnectionStatus.LOST
                await asyncio.sleep(2)
