import websockets
import asyncio
from catdog.messaging.message import Message

class Sender:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.connections = set()
        self.server = None

    async def handler(self, websocket, path):
        self.connections.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.connections.remove(websocket)

    async def start(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Sender started at ws://{self.host}:{self.port}")

    async def emit(self, message: Message):
        if self.connections:
            message_json = message.to_json()
            await asyncio.gather(*(conn.send(message_json) for conn in self.connections))

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("Sender stopped.")

