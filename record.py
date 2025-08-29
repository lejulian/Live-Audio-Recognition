import pyaudio
import webrtcvad
import wave
import os

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 480

# Ensure output directory exists
os.makedirs("wavoutput", exist_ok=True)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# List available audio devices
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

# Open stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=0)  # Replace with audio device index number

# Initialize VAD
vad = webrtcvad.Vad()
vad.set_mode(0)  #Filtering level (0-3)

def is_speech(frame, sample_rate):
    return vad.is_speech(frame, sample_rate)

def save_audio(frames, filename="output.wav"):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def record_and_save_segments():
    segment = 1
    print("Listening for speech... (Ctrl+C to stop)")
    while True:
        frames = []
        recording = False
        silence_chunks = 0
        max_silence_chunks = int(3 * RATE / CHUNK)  # 3 seconds of silence

        while True:
            try:
                frame = stream.read(CHUNK, exception_on_overflow=False)
            except Exception as e:
                print(f"Error reading audio: {e}")
                break

            if is_speech(frame, RATE):
                if not recording:
                    print(f"Recording segment {segment}...")
                    recording = True
                frames.append(frame)
                silence_chunks = 0
            else:
                if recording:
                    silence_chunks += 1
                    frames.append(frame)
                    if silence_chunks > max_silence_chunks:
                        print(f"Silence detected, evaluating segment {segment}.")
                        break

        # Only save if duration > 1.5 second
        duration_seconds = len(frames) * CHUNK / RATE
        if frames and duration_seconds > 1.5:
            save_audio(frames, filename=f"wavoutput/output_{segment}.wav")
            print(f"Audio saved as wavoutput/output_{segment}.wav")
            segment += 1
        else:
            print(f"Segment {segment} discarded (too short: {duration_seconds:.2f} seconds)")

try:
    record_and_save_segments()
except KeyboardInterrupt:
    print("Stopped by user.")