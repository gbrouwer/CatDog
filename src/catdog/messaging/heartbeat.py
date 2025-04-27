from catdog.messaging.message import Message
import json

class Heartbeat(Message):
    def __init__(self, sender, status, timestamp=None):
        content = {"status": status}  # Status: 'online', 'connected', 'receiving', 'sending'
        super().__init__(sender, content, timestamp, msg_type="heartbeat")

    @property
    def status(self):
        return self.content.get("status")

    @staticmethod
    def from_json(json_string):
        data = json.loads(json_string)
        if data.get("type") != "heartbeat":
            raise ValueError("Not a heartbeat message!")
        return Heartbeat(
            sender=data["sender"],
            status=data["content"]["status"],
            timestamp=data.get("timestamp")
        )

