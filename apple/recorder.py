#requires Blackhole installed and set up with 2 channels because tim apple is a bitch
#https://github.com/ExistentialAudio/BlackHole
#also ffmpeg too
#recorder.py

import tracks as t
import sounddevice as sd
import soundfile as sf
import time, os, subprocess
import numpy as np
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

def recorder(recLen, fileType = "wav", sample_rate = 44100, channels = 2, blocksize = 1024):
    def callback(indata, frames, time, status):
        if status:
            print(status)
        recordedChunks.append(indata.copy())

    device_index = next(
        (i for i, d in enumerate(sd.query_devices()) if "BlackHole" in d["name"]), None
    )  # Checks if blackhole is installed on device

    if device_index is None:
        raise RuntimeError("""It seems like BlackHole isn't installed :( Please install it and try again.
    
        https://github.com/ExistentialAudio/BlackHole
    
        If it is installed then check if the name of the audio device is 'BlackHole 2ch' in Audio MIDI Setup and is being used as device output.
    
        If you're not on a Mac device, please use the other version of this app""")

    if not ("BlackHole" in subprocess.check_output(["SwitchAudioSource","-t","output","-c"], text=True).strip() or "Multi-Output" in subprocess.check_output(["SwitchAudioSource","-t","output","-c"], text=True).strip()):
        raise RuntimeError("Interrupted — Check in System Settings > Sound > Output if BlackHole is selected") if input("BlackHole or a Multi-Output Device isn't detected as output device, enter [c] to cancel") == "c" else print("WARNING: BlackHole or a Multi-Output Device isn't detected as output device, audio file may return empty")
    print(f"Using device index: {device_index}")


    print(sd.query_devices())


    for i in range(int(recLen)):
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
            break