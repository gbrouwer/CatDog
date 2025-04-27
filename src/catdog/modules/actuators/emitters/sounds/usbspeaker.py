# src/catdog/modules/actuators/emitters/sounds/usbspeaker.py

from catdog.modules.actuators.emitters.sound import Sound
import os

class USBSpeakerModule(Sound):
    def __init__(self, name="usb_speaker_module", interval=0.1):
        super().__init__(name, interval)

    def emit_audio(self, audio_signal):
        """
        Play a sound. If given text, use TTS; if given a file path, play the WAV file.
        """
        if isinstance(audio_signal, str):
            if audio_signal.endswith(".wav"):
                # Play a WAV file using system command (e.g., aplay)
                os.system(f"aplay '{audio_signal}'")
            else:
                # Speak text using simple TTS (espeak)
                os.system(f'espeak "{audio_signal}"')
        else:
            print(f"[USBSpeakerModule] Unknown audio signal type: {type(audio_signal)}")

    def receive_global(self, message):
        """
        Optionally react to global emergency or broadcast messages.
        """
        print(f"[{self.name}] Received global message: {message}")

if __name__ == "__main__":
    speaker = USBSpeakerModule()
    speaker.start()

    try:
        import time
        time.sleep(1)
        speaker.actuate("Hello, I am CatDog!")
        time.sleep(1)
        speaker.actuate("/home/pi/sounds/bark.wav")
        time.sleep(1)
    finally:
        speaker.stop()
