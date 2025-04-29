import asyncio
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timezone
from messaging.heartbeat import Heartbeat

from enums import HeartbeatStatus
from messaging.message import Message  # assuming your messaging system
# import your heartbeat sender if needed (placeholder here)

class Module(ABC):
    def __init__(self, sender=None):
        self.name = self.__class__.__name__.lower()
        self.status = HeartbeatStatus.BOOTING
        self.last_status_change = datetime.now(timezone.utc)
        self.last_function = "initializing"
        self.alive = True
        self.error_info = None
        self.sender = sender  # <<<<< Add this line
        self._heartbeat_task = None

    def set_status(self, new_status: HeartbeatStatus):
        self.status = new_status
        self.last_status_change = datetime.now(timezone.utc)

    def set_last_function(self, func_name: str):
        self.last_function = func_name

    async def boot(self):
        """Optional: Override this for initial diagnostics."""
        pass

    @abstractmethod
    async def start(self):
        """Abstract: start main behavior."""
        raise NotImplementedError

    async def loop(self):
        """Optional: continuous operation."""
        while True:
            await asyncio.sleep(1)

    async def run(self):
        self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        await self.boot()
        self.set_status(HeartbeatStatus.OPERATIONAL)
        try:
            await self.start()
            await self.loop()
        except Exception as e:
            print(f"[Module:{self.name}] Main thread crashed: {e}")
            self.error_info = str(e)
            self.alive = False  # Heartbeat will notice and send final distress

    async def heartbeat_loop(self):
        while True:
            try:
                if not self.alive:
                    await self.send_heartbeat(final=True)
                    break
                await self.send_heartbeat()
            except Exception as e:
                print(f"[Heartbeat:{self.name}] Heartbeat crashed: {e}")
                break
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

    async def send_heartbeat(self, final=False):
        if self.status == HeartbeatStatus.OPERATIONAL and not final:
            heartbeat = Heartbeat(
                sender=self.name,              # <-- ADD THIS LINE
                module_name=self.name,
                status=self.status.value,
                dying=False
            )
        else:
            heartbeat = Heartbeat(
                sender=self.name,              # <-- ADD THIS LINE
                module_name=self.name,
                status=self.status.value,
                dying=final,
                last_function=self.last_function,
                active=(self.status == HeartbeatStatus.OPERATIONAL),
                connected=True,
                error=self.error_info,
                time_in_status_seconds=(datetime.now(timezone.utc) - self.last_status_change).total_seconds()
            )

        if self.sender is not None:
            await self.sender.send(heartbeat)
        else:
            print(f"[Heartbeat:{self.name}] {heartbeat.content}")
            # Example sending (replace this with actual messaging call)
            print(f"[Heartbeat:{self.name}] {heartbeat.content}")
            # Or send through websocket, local bus, etc.

            def selftest(self):
                """Optional: basic self-test."""
                print(f"[Module:{self.name}] Selftest passed.")
