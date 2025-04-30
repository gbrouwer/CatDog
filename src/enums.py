from enum import Enum

class HeartbeatStatus(Enum):
    BOOTING = "booting"
    OPERATIONAL = "operational"
    PROCESSING = "processing"
    ERROR = "error"

class ConnectionStatus(Enum):
    CONNECTED = "connected"
    LOST = "connection_lost"