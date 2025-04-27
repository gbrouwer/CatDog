# src/catdog/modules/debuggers/dummies.py

# src/catdog/modules/debuggers/dummies.py

import asyncio
import threading
import time
from catdog.module import Module
from catdog.messaging.message import Message
from catdog.messaging.receiver import Receiver
from catdog.messaging.sender import Sender
import asyncio
import threading
import time

class DummySensor(Module):
    def __init__(self, host, port, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.sender = Sender(host=self.host, port=self.port)
        self.running = False

    def start(self):
        self.running = True
        asyncio.create_task(self.sender.start())
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while self.running:
            print("[DummySensor] Capturing dummy data...")
            dummy_data = {"value": 42}
            message = Message(sender="DummySensor", content=dummy_data)
            asyncio.run(self.sender.emit(message))
            # Optionally heartbeat sending here
            time.sleep(1)

    def selftest(self):
        print("[DummySensor] Selftest passed.")

    def stop(self):
        self.running = False

# src/catdog/modules/debuggers/dummies.py


class DummyActuator(Module):
    def __init__(self, host, port, upstream=None, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.upstream = upstream
        self.receiver = None
        self.running = False

    def start(self):
        if self.upstream:
            address = f"ws://{self.upstream['host']}:{self.upstream['port']}"
            self.receiver = Receiver(address, self.handle_signal)
            asyncio.create_task(self.receiver.run())
        self.running = True
        threading.Thread(target=self.loop, daemon=True).start()

    async def handle_signal(self, message):
        print(f"[DummyActuator] Received: {message.content}")
        # Optionally heartbeat receiving here

    def loop(self):
        while self.running:
            print("[DummyActuator] Waiting for signals...")
            time.sleep(1)

    def selftest(self):
        print("[DummyActuator] Selftest passed.")

    def stop(self):
        self.running = False
