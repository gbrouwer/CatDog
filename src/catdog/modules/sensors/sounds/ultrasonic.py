from modules.sensors.sound import SoundSensor
import warnings
from gpiozero import DistanceSensor, PWMSoftwareFallback

class Ultrasonic(SoundSensor):
    def __init__(self, name="ultrasonic_sensor", trigger_pin=27, echo_pin=22, interval=0.1):
        super().__init__(name, interval)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=PWMSoftwareFallback)
        self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin, max_distance=3)

    def read(self):
        distance_cm = self.sensor.distance * 100
        return int(distance_cm)

