from module.sensors.sound import SoundSensor
import numpy as np
import threading
import pyaudio
import wave
import time

class Microphone(SoundSensor):
    def __init__(self, name="microphone_sensor", sample_rate=16000, buffer_duration=1.0, simulate=False, simulation_file=None, interval=0.1):
        super().__init__(name, interval)
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration  # seconds
        self.simulate = simulate
        self.simulation_file = simulation_file
        self.chunk_size = int(sample_rate * 0.1)  # chunk every 100ms
        self.buffer_samples = int(sample_rate * buffer_duration)
        self.buffer = np.zeros(self.buffer_samples, dtype=np.int16)
        self.audio_interface = None
        self.stream = None
        self.running = False
        self.thread = None
        self.simulated_audio = None
        self.sim_pointer = 0

    def start(self):
        if self.simulate and self.simulation_file:
            self._start_simulation()
        else:
            self._start_microphone()

    def _start_microphone(self):
        self.audio_interface = pyaudio.PyAudio()
        self.stream = self.audio_interface.open(format=pyaudio.paInt16,
                                                channels=1,
                                                rate=self.sample_rate,
                                                input=True,
                                                frames_per_buffer=self.chunk_size)
        self.running = True
        self.thread = threading.Thread(target=self._listen_microphone)
        self.thread.start()

    def _listen_microphone(self):
        while self.running:
            data = np.frombuffer(self.stream.read(self.chunk_size, exception_on_overflow=False), dtype=np.int16)
            self.buffer = np.roll(self.buffer, -len(data))
            self.buffer[-len(data):] = data

    def _start_simulation(self):
        wf = wave.open(self.simulation_file, 'rb')
        raw_data = wf.readframes(wf.getnframes())
        self.simulated_audio = np.frombuffer(raw_data, dtype=np.int16)
        self.sim_pointer = 0
        self.running = True
        self.thread = threading.Thread(target=self._simulate_audio)
        self.thread.start()

    def _simulate_audio(self):
        while self.running:
            end_pointer = self.sim_pointer + self.chunk_size
            if end_pointer > len(self.simulated_audio):
                self.sim_pointer = 0  # loop the audio
                end_pointer = self.chunk_size
            data = self.simulated_audio[self.sim_pointer:end_pointer]
            self.sim_pointer = end_pointer
            self.buffer = np.roll(self.buffer, -len(data))
            self.buffer[-len(data):] = data
            time.sleep(self.chunk_size / self.sample_rate)

    def read(self):
        return np.copy(self.buffer)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio_interface:
            self.audio_interface.terminate()