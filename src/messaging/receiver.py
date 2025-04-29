# src/messaging/receiver.py

import asyncio
import websockets
import json

class Receiver:
    def __init__(self, global_channel_url, on_message_callback):
        """
        :param global_channel_url: The websocket URL of the Global Channel (e.g., ws://localhost:9000)
        :param on_message_callback: Function to call with each received message (dict)
        """
        self.global_channel_url = global_channel_url
        self.on_message_callback = on_message_callback
        self.websocket = None
        self.connected = False

    async def run(self):
        print(f"[Receiver] Connecting to Global Channel at {self.global_channel_url}")
        async for websocket in websockets.connect(self.global_channel_url):
            self.websocket = websocket
            print("[Receiver] Connected.")
            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self.on_message_callback(data)
                    except json.JSONDecodeError:
                        print(f"[Receiver] Invalid JSON message: {message}")
            except websockets.ConnectionClosed:
                print("[Receiver] Connection lost, retrying...")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"[Receiver] Unexpected error: {e}")
                await asyncio.sleep(2)
