#requires Blackhole installed and set up with 2 channels because tim apple is a bitch
#https://github.com/ExistentialAudio/BlackHole
#also ffmpeg too


import tracks as t
import sounddevice as sd
import soundfile as sf
import time, os, subprocess
import numpy as np
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error

device_index = next(
    (i for i, d in enumerate(sd.query_devices()) if "BlackHole" in d["name"]), None
)  # Checks if blackhole is installed on device

if device_index is None:
    raise RuntimeError("""It seems like BlackHole isn't installed :( Please install it and try again.

    https://github.com/ExistentialAudio/BlackHole

    If it is installed then check if the name of the audio device is 'BlackHole 2ch' in Audio MIDI Setup

    If you're not on a Mac device, please use the other version""")

print(f"Using device index: {device_index}")


sample_rate = 44100
channels = 2
blocksize = 1024

print(sd.query_devices())

fileType = input("Enter which file type you want exported to (default: .wav) (supported: .wav (no metadata), .mp3)_ ")

def callback(indata, frames, time, status):
    if status:
        print(status)
    recordedChunks.append(indata.copy())


for i in range(int(input("Amount of tracks to record_"))):
    interrupted = False
    t.pause()
    duration = t.getDuration()
    if t.getPosition() != 0:
        t.setPlayerPos(0)
    title = t.getTitle()
    artist = t.getArtist()
    album = t.getAlbum()
    recordedChunks = []
    t.play()
    print(f"Currently recording {t.getTitle()} by {t.getArtist()} with length of {t.getDuration()} seconds; Pause music to stop recording")
    with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=callback,
            blocksize=blocksize,
        device=device_index,
        dtype='float32'
    ):
        start_time = time.time()
        time.sleep(1)
        while t.isPlaying() and (time.time() - start_time) < duration:
            time.sleep(0.1)
        print("Recording stopped")
    interrupted = t.isPlaying() == False and (time.time() - start_time) < duration

    audio = np.concatenate(recordedChunks, axis=0)
    if not interrupted:
        sf.write(f"{title} — {artist}.wav", audio, sample_rate)
        if fileType == "wav":
            print(f"Saved as '{title} — {artist}.wav'. If audio is blank, check if 'BlackHole 2ch' or a multi-output device with it is being used for sound output in Audio MIDI Setup")
        else:
            subprocess.run(["ffmpeg", "-y", "-i", f"{title} — {artist}.wav", "-codec:a", "libmp3lame", "-qscale:a", "0", f"{title} — {artist}.mp3"])
            os.remove(f"{title} — {artist}.wav")
            print(f"Saved as '{title} — {artist}.mp3'. If audio is blank, check if 'BlackHole 2ch' or a multi-output device with it is being used for sound output in Audio MIDI Setup")
            print("Writing metadata...")
            file = EasyID3(f"{title} — {artist}.mp3")
            file["title"] = title
            file["artist"] = artist
            file["album"] = album
            file.save()
            file = ID3(f"{title} — {artist}.mp3")
            if t.fetchAlbumCover(title, artist, album, "cover.jpg") != None:
                with open("cover.jpg", "rb") as albumArt:
                    file.add(APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc=f"Cover of {title} — {artist}",
                        data=albumArt.read()
                    ))
                file.save()
            print("Metadata saved")
            try:
                os.remove("cover.jpg")
            except FileNotFoundError:
                pass

    else:
        print("Recording not saved due to user interrupt")