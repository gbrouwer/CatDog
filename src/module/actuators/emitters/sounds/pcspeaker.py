import asyncio
import winsound
import os
from module.actuators.emitters.sounds.sound import Sound  # Base SoundEmitter
from messaging.receiver import Receiver
from asset_manager import AssetManager

class PCSpeaker(Sound):
    def __init__(self, host, port, upstream=None, sound_path='sounds/boot.wav', **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.upstream = upstream
        self.sound_path = AssetManager.resolve(*sound_path.split("/"))
        self.receiver = None
        self.running = False
        self.is_playing = False

    async def boot(self):
        self.set_last_function("booting diagnostics")
        print("[PCSpeaker] Booting: Playing diagnostic sound...")
        if not os.path.isfile(self.sound_path):
            raise RuntimeError(f"[PCSpeaker] Boot file not found: {self.sound_path}")
        try:
            winsound.PlaySound(self.sound_path, winsound.SND_FILENAME)
        except Exception as e:
            raise RuntimeError(f"[PCSpeaker] Boot failed: {e}")

    async def start(self):
        self.running = True
        self.set_status(HeartbeatStatus.OPERATIONAL)
        if self.upstream:
            address = f"ws://{self.upstream['host']}:{self.upstream['port']}"
            self.receiver = Receiver(address, self.receive)
            asyncio.create_task(self.receiver.run())
        asyncio.create_task(self.loop())

    async def receive(self, message):
        self.set_last_function("processing received message")
        if self.is_playing:
            return

        if isinstance(message.content, dict) and message.content.get("play_sound", False):
            try:
                self.set_status(HeartbeatStatus.PROCESSING)
                self.is_playing = True
                winsound.PlaySound(self.sound_path, winsound.SND_FILENAME)
            finally:
                self.is_playing = False
                self.set_status(HeartbeatStatus.OPERATIONAL)

    async def loop(self):
        while self.running:
            self.set_last_function("idle loop")
            await asyncio.sleep(1)

    def selftest(self):
        print("[PCSpeaker] Selftest passed.")

    async def stop(self):
        self.running = False
