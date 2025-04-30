# src/module/actuators/emitters/sounds/sound_emitter.py

import asyncio
import os
import sounddevice as sd
import soundfile as sf

from module.actuators.emitters.sounds.sound import Sound
from messaging.sender import Sender
from messaging.module_link_client import ModuleLinkClient
from asset_manager import AssetManager
from enums import HeartbeatStatus, ConnectionStatus


class SoundEmitter(Sound):
    def __init__(self, global_channel_url, upstream_data_url):
        """
        :param global_channel_url: WebSocket URL for sending heartbeats (GCC)
        :param upstream_data_url: WebSocket URL for connecting to sensor data (module link)
        """
        super().__init__()
        self.global_channel_url = global_channel_url
        self.upstream_data_url = upstream_data_url
        self.sound_path = AssetManager.resolve("sounds", "boot.wav")
        self.sender = None
        self.data_receiver = None
        self.is_playing = False
        self.running = False
        self.audio_data = None
        self.sample_rate = None

        # Threshold logic
        self.threshold = 25          # Threshold signal strength (e.g., 25cm)
        self.signal_high = False     # Current threshold crossing state

    async def boot(self):
        self.set_last_function("booting diagnostics")
        print("[SoundEmitter] Booting: Preparing sound file...")

        if not os.path.isfile(self.sound_path):
            raise RuntimeError(f"[SoundEmitter] Boot file not found: {self.sound_path}")

        try:
            self.audio_data, self.sample_rate = sf.read(self.sound_path, dtype='float32')
            print("[SoundEmitter] Sound file loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"[SoundEmitter] Boot failed: {e}")

    async def start(self):
        self.running = True

        # Setup Sender for heartbeats
        self.sender = Sender(self.global_channel_url)
        await self.sender.connect()

        # Setup direct data Receiver (ModuleLinkClient)
        self.data_receiver = ModuleLinkClient(
            url=self.upstream_data_url,
            on_message_callback=self.handle_message,
            parent_module=self
        )
        await asyncio.sleep(2)  # let server get ready
        asyncio.create_task(self.data_receiver.run())

        self.set_status(HeartbeatStatus.OPERATIONAL)
        print("[SoundEmitter] Started successfully.")

    async def handle_message(self, msg):
        value = msg.get("value")  # raw input value
        print(f"[SoundEmitter] Received signal value: {value}")

        if value <= self.threshold and not self.signal_high:
            # Entered below threshold
            self.signal_high = True
            await self.on_threshold_enter()
        elif value > self.threshold and self.signal_high:
            # Exited threshold zone
            self.signal_high = False
            await self.on_threshold_exit()

    async def on_threshold_enter(self):
        print("[SoundEmitter] Threshold entered: Signal dropped below threshold!")
        await self.play_sound()

    async def on_threshold_exit(self):
        print("[SoundEmitter] Threshold exited: Signal rose above threshold.")
        # Optional: stop sound, or log exit

    async def play_sound(self):
        if self.is_playing:
            return  # Skip if already playing

        self.is_playing = True
        self.set_last_function("playing sound")
        self.set_status(HeartbeatStatus.PROCESSING)

        try:
            sd.play(self.audio_data, self.sample_rate, blocking=False)
            print("[SoundEmitter] Playing sound...")
            await asyncio.sleep(len(self.audio_data) / self.sample_rate)
        finally:
            self.is_playing = False
            self.set_status(HeartbeatStatus.OPERATIONAL)

    async def loop(self):
        while self.running:
            self.set_last_function("idle loop")
            await asyncio.sleep(1)

    async def stop(self):
        self.running = False
        if self.sender:
            await self.sender.close()
        print("[SoundEmitter] Stopped.")

    def selftest(self):
        print("[SoundEmitter] Selftest passed.")

    async def emit_audio(self, audio_signal):
        await self.play_sound()