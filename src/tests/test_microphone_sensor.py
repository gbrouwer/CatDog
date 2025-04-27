# src/tests/test_microphone_sensor.py

import time
import numpy as np
from catdog.modules.sensors.sounds.microphone import Microphone

def test_microphone_noise_detection():
    # You can toggle simulate=True and add a wav file path if needed
    mic = Microphone(sample_rate=16000, buffer_duration=1.0, simulate=False, simulation_file=None)
    
    mic.start()
    time.sleep(1)  # allow some buffer to fill

    audio_buffer = mic.read()
    
    mic.stop()

    # Simple test: buffer must not be all zeros
    assert isinstance(audio_buffer, np.ndarray), "Audio buffer must be a numpy array."
    assert audio_buffer.shape[0] > 0, "Audio buffer must not be empty."
    assert np.any(audio_buffer != 0), "Audio input is silent (all zeros), check microphone or simulation."

    print("[TEST PASS] Microphone captured audio successfully.")

if __name__ == "__main__":
    test_microphone_noise_detection()
