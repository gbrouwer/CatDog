from messaging.message import Message

class Heartbeat(Message):
    def __init__(
        self,
        sender: str,  # <--- ADD THIS
        module_name: str,
        status: str,
        dying: bool,
        last_function: str = None,
        active: bool = None,
        connected: bool = None,
        error: str = None,
        time_in_status_seconds: float = None
    ):
        payload = {
            "module_name": module_name,
            "status": status,
            "dying": dying
        }

        if last_function is not None:
            payload["last_function"] = last_function
        if active is not None:
            payload["active"] = active
        if connected is not None:
            payload["connected"] = connected
        if error is not None:
            payload["error"] = error
        if time_in_status_seconds is not None:
            payload["time_in_status_seconds"] = time_in_status_seconds

        super().__init__(sender=sender, content=payload)  # <-- Pass sender properly