import json
import time
import base64

class Message:
    def __init__(self, sender, content, timestamp=None, msg_type="data"):
        self.sender = sender  # Module name (e.g., "TempSensor")
        self.content = content  # dict, can contain base64-encoded fields
        self.timestamp = timestamp or time.time()
        self.msg_type = msg_type  # 'data' or 'heartbeat'

    def to_dict(self):
        return {
            "sender": self.sender,
            "timestamp": self.timestamp,
            "type": self.msg_type,
            "content": self.content,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string):
        data = json.loads(json_string)
        return Message(
            sender=data["sender"],
            content=data["content"],
            timestamp=data.get("timestamp"),
            msg_type=data.get("type", "data")
        )

    @staticmethod
    def encode_binary_data(binary_data):
        return base64.b64encode(binary_data).decode('utf-8')

    @staticmethod
    def decode_binary_data(encoded_string):
        return base64.b64decode(encoded_string)

