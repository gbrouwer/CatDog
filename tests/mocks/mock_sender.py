# tests/mocks/mock_sender.py

class MockSender:
    def __init__(self):
        self.sent_messages = []

    async def send(self, message):
        """Simulate sending a message by storing it locally."""
        self.sent_messages.append(message)
