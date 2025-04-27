# src/catdog/module.py

import threading
import time
from abc import ABC, abstractmethod

# Global Emergency Bus for critical system-wide broadcasts
class GlobalBus:
    messages = []

    @classmethod
    def broadcast(cls, message):
        cls.messages.append(message)

    @classmethod
    def get_messages(cls):
        return list(cls.messages)

class Module(ABC):
    def __init__(self, name="module", interval=0.1):
        self.name = name
        self.interval = interval
        self.running = False

        self.input_queue = []  # Queue of Message objects
        self.output_queue = []  # Queue of Message objects to send

        self.upstream_subscriptions = []  # Specific modules to listen to
        self.downstream_subscriptions = []  # Specific modules to broadcast to

        self.listen_thread = None
        self.broadcast_thread = None
        self.globalbus_check_thread = None

        self.agent = None  # Will be set when Agent builds modules
        self.last_heartbeat_time = time.time()
        self.heartbeat_interval = 5  # seconds

    def start(self):
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen)
        self.broadcast_thread = threading.Thread(target=self._broadcast)
        self.globalbus_check_thread = threading.Thread(target=self._globalbus_check)
        self.listen_thread.start()
        self.broadcast_thread.start()
        self.globalbus_check_thread.start()

    def stop(self):
        self.running = False
        if self.listen_thread:
            self.listen_thread.join()
        if self.broadcast_thread:
            self.broadcast_thread.join()
        if self.globalbus_check_thread:
            self.globalbus_check_thread.join()

    def _listen(self):
        while self.running:
            if self.input_queue:
                message = self.input_queue.pop(0)
                self.receive(message)
            time.sleep(self.interval)

    def _broadcast(self):
        while self.running:
            # Broadcast new output messages
            if self.output_queue:
                message = self.output_queue.pop(0)
                for module in self.downstream_subscriptions:
                    module.input_queue.append(message)

            # Send heartbeat
            current_time = time.time()
            if current_time - self.last_heartbeat_time > self.heartbeat_interval:
                if self.agent:
                    self.agent.update_heartbeat(self.name)
                self.last_heartbeat_time = current_time

            time.sleep(self.interval)

    def _globalbus_check(self):
        while self.running:
            messages = GlobalBus.get_messages()
            for message in messages:
                self.receive_global(message)
            time.sleep(self.interval)

    def subscribe_upstream(self, module):
        self.upstream_subscriptions.append(module)

    def subscribe_downstream(self, module):
        self.downstream_subscriptions.append(module)

    def send_output(self, content):
        message = Message(sender=self.name, content=content)
        self.output_queue.append(message)

    @abstractmethod
    def receive(self, message):
        """
        Handle incoming Message from upstream modules.
        """
        pass

    def receive_global(self, message):
        """
        Handle incoming emergency/global messages.
        Override if module cares about GlobalBus signals.
        """
        pass
