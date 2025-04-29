from module.actuators.emitters.sounds.pcspeaker import PCSpeaker

# Create an instance
speaker = PCSpeaker(
    host="127.0.0.1",
    port=9003,
    sound_path="assets/sounds/boot.wav"
)

# Call test method
speaker.test_play_boot_sound()