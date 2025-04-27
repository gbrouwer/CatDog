from modules.actuators.displacer import Displacer

class ServoModule(Displacer):
    def __init__(self, name="servo_module", interval=0.1):
        super().__init__(name, interval)
        self.angle = 0

    def displace(self, displacement_signal):
        self.angle = displacement_signal
        print(f"[ServoModule] Set angle to: {self.angle} degrees")

if __name__ == "__main__":
    servo = ServoModule(interval=0.5)
    servo.start()

    try:
        import time
        time.sleep(2)
        servo.actuate(90)
        time.sleep(2)
        servo.actuate(0)
        time.sleep(2)
    finally:
        servo.stop()
