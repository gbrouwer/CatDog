import asyncio
import time
module import Module
messaging.sender import Sender
messaging.receiver import Receiver
messaging.message import Message
import asyncio

class DummySensor(Module):
    def __init__(self, host, port, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.sender = Sender(host=self.host, port=self.port)
        self.running = False

    async def start(self):
        print("Started sensor")
        self.running = True
        await self.sender.start()
        asyncio.create_task(self.loop())

    async def loop(self):
        while self.running:
            print("[DummySensor] Capturing dummy data...")
            dummy_data = {
                "value": 42,
                "play_sound": True  # <-- Important flag for PCSPEAKER
            }
            message = Message(sender="DummySensor", content=dummy_data)
            await self.sender.emit(message)
            await asyncio.sleep(5)

    async def receive(self, message):
        print(f"[DummySensor] (Dummy) Received message: {message.content}")

    def selftest(self):
        print("[DummySensor] Selftest passed.")

    async def stop(self):
        self.running = False
        print("[DummySensor] Stopped.")


class DummyActuator(Module):
    def __init__(self, host, port, upstream=None, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.upstream = upstream
        self.receiver = None
        self.running = False

    async def start(self):
        self.running = True
        if self.upstream:
            address = f"ws://{self.upstream['host']}:{self.upstream['port']}"
            self.receiver = Receiver(address, self.receive)
            asyncio.create_task(self.receiver.run())
        asyncio.create_task(self.loop())

    async def receive(self, message):
        print(f"[DummyActuator] Received: {message.content}")

    async def loop(self):
        while self.running:
            print("[DummyActuator] Waiting for signals...")
            await asyncio.sleep(1)

    def selftest(self):
        print("[DummyActuator] Selftest passed.")

    async def stop(self):
        self.running = False
