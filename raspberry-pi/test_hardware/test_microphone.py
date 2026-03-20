import pyaudio
import wave
import numpy as np

chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 16000
record_seconds = 3

p = pyaudio.PyAudio()

print("\nAvailable audio devices:")
for i in range(p.get_device_count()):
	info = p.get_device_info_by_index(i)
	if info['maxInputChannels'] > 0:
		print(f"[{i}] {info['name']}")

print(f"\nRecording {record_seconds} seconds...")
print("Speak into mic")

try:
	stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
	frames = []

	for i in range(0, int(rate / chunk * record_seconds)):
		data = stream.read(chunk)
		frames.append(data)
	print("\nRecording complete")

	stream.stop_stream()
	stream.close()

	# analyse audio level
	audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
	max_amplitude = np.max(np.abs(audio_data))

	print(f"\nAudio Analysis:")
	print(f"Max Amplitude: {max_amplitude}")

	if max_amplitude > 1000:
		print("Good audio level")
	else:
		print("Audio level low")

	output_file = "/home/danellepi/echocare/test_recording.wav"
	wf = wave.open(output_file, 'wb')
	wf.setnchannels(channels)
	wf.setsampwidth(p.get_sample_size(format))
	wf.setframerate(rate)
	wf.writeframes(b''.join(frames))
	wf.close()
	print(f"\n Saved to: {output_file}")

except Exception as e:
	print(f"\nError: {e}")

finally:
	p.terminate()
	print("Test complete")
