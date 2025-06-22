#requires Blackhole installed and set up with 2 channels because tim apple is a bitch
#https://github.com/ExistentialAudio/BlackHole

import tracks as t
import sounddevice as sd
import soundfile as sf

t.pause()
duration = t.getDuration()
if t.getPosition() != 0:
    t.setPlayerPos(0)
sample_rate = 44100
channels = 2

print(sd.query_devices())


device_index = next(
    (i for i, d in enumerate(sd.query_devices()) if "BlackHole" in d["name"]), None
) #Checks if blackhole is installed on device

if device_index is None:
    raise RuntimeError("""It seems like BlackHole isn't installed :( Please install it and try again.
    
    https://github.com/ExistentialAudio/BlackHole
    
    If it is installed then check if the name of the audio device is 'BlackHole 2ch' in Audio MIDI Setup
    
    If you're not on a Mac device, please use the other version""")


print(f"Using device index: {device_index}")

audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float32', device=device_index)
t.play()


sd.wait()

sf.write("output.wav", audio, sample_rate)