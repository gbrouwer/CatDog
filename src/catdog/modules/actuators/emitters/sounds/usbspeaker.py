from catdog.modules.actuators.emitters.sound import SoundEmitter
import os

class USBSpeaker(SoundEmitter):
    def __init__(self, name="usb_speaker_module", interval=0.1):
        super().__init__(name, interval)

    def emit_audio(self, audio_signal):
        if audio_signal.endswith(".wav"):
            # Play a WAV file
            os.system(f"aplay {audio_signal}")
        else:
            # Speak text using espeak (simple TTS)
            os.system(f'espeak "{audio_signal}"')

if __name__ == "__main__":
    speaker = USBSpeaker()
    speaker.start()

    try:
        speaker.actuate("Hello, I am CatDog!")  # Speak text
        speaker.actuate("/home/pi/sounds/bark.wav")  # Play WAV file
    finally:
        speaker.stop()