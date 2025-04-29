import asyncio
import pytest
from tests.mocks.mock_sender import MockSender
from enums import HeartbeatStatus
from module.module import Module
from datetime import datetime, timezone, timezone

# Define a simple dummy module for testing
class DummyModule(Module):
    async def start(self):
        pass

@pytest.mark.asyncio
async def test_module_sends_normal_heartbeat():
    mock_sender = MockSender()
    module = DummyModule(sender=mock_sender)

    # Manually set to operational for clean minimal heartbeat
    module.set_status(HeartbeatStatus.OPERATIONAL)
    
    await module.send_heartbeat()

    # Check if one message was sent
    assert len(mock_sender.sent_messages) == 1

    heartbeat = mock_sender.sent_messages[0]

    # Check minimal fields
    assert heartbeat.content["module_name"] == "dummymodule"
    assert heartbeat.content["status"] == "operational"
    assert heartbeat.content["dying"] is False

    # Should NOT contain diagnostic fields
    assert "last_function" not in heartbeat.content
    assert "error" not in heartbeat.content

@pytest.mark.asyncio
async def test_module_sends_distress_heartbeat():
    mock_sender = MockSender()
    module = DummyModule(sender=mock_sender)

    # Simulate crash
    module.set_status(HeartbeatStatus.ERROR)
    module.error_info = "Simulated Crash"

    await module.send_heartbeat(final=True)

    # Check if one message was sent
    assert len(mock_sender.sent_messages) == 1

    heartbeat = mock_sender.sent_messages[0]

    # Check distress heartbeat fields
    assert heartbeat.content["module_name"] == "dummymodule"
    assert heartbeat.content["status"] == "error"
    assert heartbeat.content["dying"] is True
    assert heartbeat.content["error"] == "Simulated Crash"
    assert "last_function" in heartbeat.content
