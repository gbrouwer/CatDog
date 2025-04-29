from module.sensor import Sensor

class SoundSensor(Sensor):
    def __init__(self, name="sound_sensor", interval=0.1):
        super().__init__(name, interval)
