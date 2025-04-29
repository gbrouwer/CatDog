from enum import Enum

class HeartbeatStatus(Enum):
    BOOTING = "booting"
    OPERATIONAL = "operational"
    PROCESSING = "processing"
    ERROR = "error"
