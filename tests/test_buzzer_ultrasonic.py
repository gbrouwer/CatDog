from modules.actuators.emitters.sounds import Buzzer
from modules.sensors.sounds import UltraSonic

# Example test runner
if __name__ == "__main__":
    import time

    ultrasonic = UltraSonic()
    buzzer = Buzzer()

    ultrasonic.start()
    buzzer.start()

    try:
        while True:
            distance = ultrasonic.read()
            print(f"Distance: {distance} cm")

            if distance < 20:
                buzzer.actuate("1")
            else:
                buzzer.actuate("0")

            time.sleep(0.1)

    finally:
        ultrasonic.stop()
        buzzer.stop()
