# src/catdog/modules/actuators/emitter.py

from module.actuator import Actuator
from abc import ABC, abstractmethod

class Emitter(Actuator, ABC):
    def __init__(self, name="emitter", interval=0.1):
        super().__init__(name, interval)

    @abstractmethod
    def emit_signal(self, signal):
        """
        Emit a signal into the environment (light, sound, etc.).
        """
        pass

    def actuate(self, command):
        """
        When actuating, emit the given signal.
        """
        self.emit_signal(command)

    def receive_global(self, message):
        """
        Optionally react to global emergency or broadcast messages.
        Override if needed.
        """
        print(f"[{self.name}] Received global message: {message}")
