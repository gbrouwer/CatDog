from modules.actuators.emitter import Emitter
from abc import abstractmethod
import threading
import time

class Sound(Emitter):
    def __init__(self, name="sound_emitter", interval=0.1):
        super().__init__(name, interval)
        self.running = False
        self.listen_thread = None
        self.broadcast_thread = None

    @abstractmethod
    def emit_audio(self, audio_signal):
        """
        Emit an audio signal into the environment.
        """
        pass

    def emit_signal(self, signal):
        self.emit_audio(signal)

    def start(self):
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen)
        self.broadcast_thread = threading.Thread(target=self._broadcast)
        self.listen_thread.start()
        self.broadcast_thread.start()

    def stop(self):
        self.running = False
        if self.listen_thread:
            self.listen_thread.join()
        if self.broadcast_thread:
            self.broadcast_thread.join()

    def _listen(self):
        while self.running:
            # Placeholder: Listening logic (to be expanded in child classes)
            time.sleep(self.interval)

    def _broadcast(self):
        while self.running:
            # Placeholder: Broadcasting logic (to be expanded in child classes)
            time.sleep(self.interval)
