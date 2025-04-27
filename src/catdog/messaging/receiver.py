import websockets
import asyncio

from catdog.messaging.message import Message

class Receiver:
    def __init__(self, uri, on_message_callback):
        self.uri = uri
        self.on_message_callback = on_message_callback
        self.connection = None

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            self.connection = websocket
            print(f"Connected to {self.uri}")
            await self.listen()

    async def listen(self):
        try:
            async for message_json in self.connection:
                message = Message.from_json(message_json)
                await self.on_message_callback(message)
        except websockets.ConnectionClosed:
            print(f"Connection closed: {self.uri}")

    async def run(self):
        while True:
            try:
                await self.connect()
            except Exception as e:
                print(f"Connection error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
