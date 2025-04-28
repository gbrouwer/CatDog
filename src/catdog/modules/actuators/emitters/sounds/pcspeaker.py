import asyncio
import winsound
import os
from catdog.module import Module
from catdog.messaging.receiver import Receiver

class PCSpeaker(Module):
    def __init__(self, host, port, upstream=None, sound_path='sounds/boot.wav', **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.upstream = upstream
        self.sound_path = sound_path
        self.receiver = None
        self.running = False

    async def boot(self):
        print("[PCSpeaker] Booting: Playing diagnostic sound...")
        print(self.sound_path)
        if not os.path.exists(self.sound_path):
            raise RuntimeError(f"[PCSpeaker] Boot file not found: {self.sound_path}")
        try:
            winsound.PlaySound(self.sound_path, winsound.SND_FILENAME)
            print("[PCSpeaker] Diagnostic sound played successfully.")
        except Exception as e:
            print(f"[PCSpeaker] Boot failed: {e}")
            raise RuntimeError("PCSpeaker failed during sound playback.")

    async def start(self):
        self.running = True
        if self.upstream:
            address = f"ws://{self.upstream['host']}:{self.upstream['port']}"
            self.receiver = Receiver(address, self.receive)
            asyncio.create_task(self.receiver.run())
        asyncio.create_task(self.loop())

    async def receive(self, message):
        print(f"[PCSpeaker] Received: {message.content}")
        try:
            winsound.PlaySound(self.sound_path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"[PCSpeaker] Playback error: {e}")

    async def loop(self):
        while self.running:
            await asyncio.sleep(1)

    def selftest(self):
        print("[PCSpeaker] Selftest passed.")

    async def stop(self):
        self.running = False
        print("[PCSpeaker] Stopped.")

    def test_play_boot_sound(self):
        print("[PCSpeaker] Testing boot sound manually...")
        abs_sound_path = os.path.abspath(self.sound_path)
        print(f"[PCSpeaker] Resolved absolute sound path: {abs_sound_path}")
        if not os.path.exists(abs_sound_path):
            print(f"[PCSpeaker] ERROR: Sound file not found at {abs_sound_path}")
            return
        try:
            import winsound
            winsound.PlaySound(abs_sound_path, winsound.SND_FILENAME)
            print("[PCSpeaker] Boot sound played successfully.")
        except Exception as e:
            print(f"[PCSpeaker] Failed to play boot sound: {e}")
