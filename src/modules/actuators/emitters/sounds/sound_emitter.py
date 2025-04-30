# src/module/actuators/emitters/sounds/sound_emitter.py

import asyncio
import os
import sounddevice as sd
import soundfile as sf
import datetime

from modules.actuators.emitters.sounds.sound import Sound
from messaging.sender import Sender
from messaging.module_link_client import ModuleLinkClient
from asset_manager import AssetManager
from enums import HeartbeatStatus, ConnectionStatus
from log import log, log_error


class SoundEmitter(Sound):
    def __init__(self, global_channel_url, upstream_data_url):
        """
        :param global_channel_url: WebSocket URL for sending heartbeats (GCC)
        :param upstream_data_url: WebSocket URL for connecting to sensor data (module link)
        """
        super().__init__()
        self.global_channel_url = global_channel_url
        self.upstream_data_url = upstream_data_url
        self.sound_path = AssetManager.resolve("sounds", "boot-01.wav")
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
        log("SoundEmitter", "Booting: Preparing sound file...")

        if not os.path.isfile(self.sound_path):
            raise RuntimeError(f"[SoundEmitter] Boot file not found: {self.sound_path}")

        try:
            self.audio_data, self.sample_rate = sf.read(self.sound_path, dtype='float32')
            log("SoundEmitter", "Sound file loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"[SoundEmitter] Boot failed: {e}")

    async def start(self):
        self.running = True

        # Setup Sender for heartbeats
        self.sender = Sender(self.global_channel_url,"SoundEmitter")
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
        log("SoundEmitter", "Started successfully.")

    async def handle_message(self, msg):
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')
        log("SoundEmitter", f"{timestamp} - Incoming message: {msg}")

        if "value" not in msg:
            log("SoundEmitter", "Warning: Incoming message has no 'value' field!")
            return

        value = msg["value"]
        log("SoundEmitter", f"Parsed signal value: {value} cm")

        if value <= self.threshold and not self.signal_high:
            log("SoundEmitter", f"Detected entry: value={value} <= threshold={self.threshold}")
            self.signal_high = True
            await self.on_threshold_enter()
        elif value > self.threshold and self.signal_high:
            log("SoundEmitter", f"Detected exit: value={value} > threshold={self.threshold}")
            self.signal_high = False
            await self.on_threshold_exit()
        else:
            log("SoundEmitter", f"No threshold transition. Current state: signal_high={self.signal_high}")

    async def on_threshold_enter(self):
        log("SoundEmitter", "Threshold entered: Signal dropped below threshold!")
        await self.play_sound()

    async def on_threshold_exit(self):
        log("SoundEmitter", "Threshold exited: Signal rose above threshold.")
        # Optional: stop sound, or log exit

    async def play_sound(self):
        if self.is_playing:
            return  # Skip if already playing

        self.is_playing = True
        self.set_last_function("playing sound")
        self.set_status(HeartbeatStatus.PROCESSING)

        try:
            sd.play(self.audio_data, self.sample_rate, blocking=False)
            log("SoundEmitter", "Playing sound...")
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
        log("SoundEmitter", "Stopped.")

    def selftest(self):
        log("SoundEmitter", "Selftest passed.")

    async def emit_audio(self, audio_signal):
        await self.play_sound()