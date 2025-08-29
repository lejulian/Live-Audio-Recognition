import subprocess

# Start record.py (records and saves wav files to wavoutput/)
record_proc = subprocess.Popen(["python3", "record.py"])

# Start transcribe.py (continuously transcribes and deletes wav files in wavoutput/)
transcribe_proc = subprocess.Popen(["python3", "transcribe.py"])

try:
    record_proc.wait()
    transcribe_proc.wait()
except KeyboardInterrupt:
    print("Stopping both processes...")
    record_proc.terminate()
    transcribe_proc.terminate()