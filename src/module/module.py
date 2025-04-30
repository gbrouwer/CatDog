import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from enums import HeartbeatStatus, ConnectionStatus
from messaging.heartbeat import Heartbeat





class Module(ABC):
    
    def __init__(self, name=None, interval=0.1, sender=None):
        self.name = name if name else self.__class__.__name__.lower()
        self.interval = interval
        self.status = HeartbeatStatus.BOOTING
        self.last_status_change = datetime.now(timezone.utc)
        self.last_function = "initializing"
        self.alive = True
        self.error_info = None
        self.connection_status = ConnectionStatus.LOST
        self.sender = sender
        self._heartbeat_task = None

    def set_status(self, new_status: HeartbeatStatus):
        self.status = new_status
        self.last_status_change = datetime.now(timezone.utc)

    def set_last_function(self, func_name: str):
        self.last_function = func_name

    async def boot(self):
        """Optional override: diagnostic and setup phase."""
        pass

    @abstractmethod
    async def start(self):
        """Must be overridden: prepare and launch core logic."""
        ...

    async def loop(self):
        """Optional: override for continuous execution."""
        while self.alive:
            self.set_last_function("idle loop")
            await asyncio.sleep(1)

    async def run(self):
        """Entrypoint for all modules: boots, starts, loops, and runs heartbeat."""
        self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        try:
            await self.boot()
            self.set_status(HeartbeatStatus.OPERATIONAL)
            await self.start()
            await self.loop()
        except Exception as e:
            print(f"[Module:{self.name}] Main thread crashed: {e}")
            self.error_info = str(e)
            self.alive = False  # Heartbeat loop will detect and shut down

    async def heartbeat_loop(self):
        while True:
            try:
                if not self.alive:
                    await self.send_heartbeat(final=True)
                    break
                await self.send_heartbeat()
            except Exception as e:
                print(f"[Heartbeat:{self.name}] Error sending heartbeat: {e}")
                break
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

    async def send_heartbeat(self, final=False):
        if self.sender is None:
            print(f"[Heartbeat:{self.name}] No sender attached.")
            return

        heartbeat = Heartbeat(
            sender=self.name,
            module_name=self.name,
            status=self.status.value,
            dying=final
        )

        # Only send diagnostic fields if needed
        if self.status != HeartbeatStatus.OPERATIONAL or final:
            heartbeat.content.update({
                "last_function": self.last_function,
                "active": (self.status == HeartbeatStatus.OPERATIONAL),
                "connected": (self.connection_status == ConnectionStatus.CONNECTED),
                "error": self.error_info,
                "time_in_status_seconds": (datetime.now(timezone.utc) - self.last_status_change).total_seconds()
            })

        await self.sender.send(heartbeat)

    def selftest(self):
        print(f"[{self.name}] Selftest passed.")
