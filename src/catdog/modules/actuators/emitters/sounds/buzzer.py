from modules.actuators.emitters import SoundEmitter
from gpiozero import Buzzer as GPIOBuzzer

class Buzzer(SoundEmitter):
    def __init__(self, name="buzzer_module", pin=17, interval=0.1):
        super().__init__(name, interval)
        self.buzzer = GPIOBuzzer(pin)

    def emit_audio(self, audio_signal):
        if audio_signal != "0":
            self.buzzer.on()
        else:
            self.buzzer.off()
