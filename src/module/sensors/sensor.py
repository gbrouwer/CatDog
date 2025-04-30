from module import Module

class Sensor(Module):
    def __init__(self, name="sensor", interval=0.1):
        super().__init__(name, interval)
