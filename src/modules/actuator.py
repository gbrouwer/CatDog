# src/catdog/modules/actuator.py

from modules.module import Module
from abc import ABC, abstractmethod

class Actuator(Module, ABC):
    def __init__(self, name="actuator", interval=0.1):
        super().__init__(name, interval)

    @abstractmethod
    def actuate(self, command):
        """
        Perform an action based on a command.
        """
        pass

    def receive(self, data):
        """
        Default behavior when receiving data: Actuate based on it.
        """
        self.actuate(data)

    def receive_global(self, message):
        """
        Optionally react to global emergency or broadcast messages.
        Override if needed.
        """
        print(f"[{self.name}] Received global message: {message}")
