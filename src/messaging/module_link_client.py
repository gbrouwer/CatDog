# src/messaging/module_link_client.py

import asyncio
import websockets
import json

class ModuleLinkClient:
    def __init__(self, url, on_message_callback, parent_module=None):
        self.url = url
        self.on_message_callback = on_message_callback
        self.parent = parent_module  # Optional: for updating connection status

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.url) as websocket:
                    print(f"[ModuleLinkClient] Connected to {self.url}")
                    if self.parent:
                        self.parent.connection_status = "connected"

                    async for message in websocket:
                        try:
                            payload = json.loads(message)
                            await self.on_message_callback(payload)
                        except Exception as e:
                            print(f"[ModuleLinkClient] Failed to handle message: {e}")

            except Exception as e:
                print(f"[ModuleLinkClient] Connection error: {e}")
                if self.parent:
                    self.parent.connection_status = "disconnected"
                await asyncio.sleep(2)
