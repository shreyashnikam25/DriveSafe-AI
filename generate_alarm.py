import wave
import math
import struct

def generate_alarm():
    sample_rate = 44100
    duration = 1.0  # 1 second loop
    frequency = 1000.0  # Loud, clear frequency

    num_samples = int(sample_rate * duration)
    
    with wave.open("alarm.wav", "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            # Generate clean sine wave
            sample = math.sin(2 * math.pi * frequency * i / sample_rate)
            # Modulate amplitude slightly to create a smooth siren pulse
            modulation = math.sin(2 * math.pi * 4 * i / sample_rate)  # 4Hz pulse rate
            value = int(32767 * 0.6 * sample * (0.8 + 0.2 * modulation))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

    print("alarm.wav generated successfully in S:\\DriveSafe-AI\\")

if __name__ == "__main__":
    generate_alarm()