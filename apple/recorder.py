#requires Blackhole installed and set up with 2 channels because tim apple is a bitch
#https://github.com/ExistentialAudio/BlackHole
#also ffmpeg too
#recorder.py
import os
import subprocess
from time import sleep, time

import numpy as np
import sounddevice as sd
import soundfile as sf
import tracks as t
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3
from mutagen.oggvorbis import OggVorbis


def recorder(track_count,
             fileType="wav",
             sample_rate=44100,
             channels=2,
             blocksize=1024,
             skipWarning=False,
             outputDir=".",
             adSkip=True):
    os.makedirs(outputDir, exist_ok=True)

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recordedChunks.append(indata.copy())

    device_index = check_blackhole()

    if not skipWarning and not check_blackhole_selected():
        if input(
                "BlackHole or a Multi-Output Device isn't detected as output device, enter [c] to cancel. Enter anything else to proceed_ "
        ) == "c":
            raise RuntimeError(
                "Interrupted — Check in System Settings > Sound > Output if BlackHole is selected"
            )
        print(
            "WARNING: BlackHole or a Multi-Output Device isn't detected as output device, audio file may return empty"
        )

    print(f"Using device index: {device_index}")

    print(sd.query_devices())

    for i in range(int(track_count)):
        interrupted = False
        t.pause()
        duration = t.getDuration()
        if t.getPosition() != 0:
            t.setPlayerPos(0)
        title = t.getTitle()
        artist = t.getArtist()
        album = t.getAlbum()

        while t.adLikely() and adSkip:
            t.play()
            print("Advertisement likely, skipping recording for track")
            sleep(t.getDuration())

        recordedChunks = []
        t.play()

        print(
            f"Currently recording {title} by {artist} with length of {t.getDuration()} seconds; Pause music to stop recording"
        )

        with sd.InputStream(samplerate=sample_rate,
                            channels=channels,
                            callback=callback,
                            blocksize=blocksize,
                            device=device_index,
                            dtype='float32'):
            start_time = time()
            sleep(1)
            while t.isPlaying() and (time() - start_time) < duration:
                sleep(0.1)
            print("Recording stopped")

        interrupted = not t.isPlaying() and (time() - start_time) < duration

        if interrupted:
            print("Recording not saved due to user interrupt")
            break

        audio = np.concatenate(recordedChunks, axis=0)

        wav_file = f"{outputDir}/{title} — {artist}.wav"
        file_name = f"{title} — {artist}.{fileType}"
        file_path = f"{outputDir}/{file_name}"

        sf.write(wav_file, audio, sample_rate)

        saved_as = f"Saved as '{file_name}' in {outputDir}/. If audio is blank, check if 'BlackHole 2ch' or a multi-output device with it is being used for sound output in Audio MIDI Setup"

        if fileType == "wav":
            print(saved_as)

        if fileType == "mp3":
            subprocess.run([
                "ffmpeg", "-y", "-i", wav_file, "-codec:a", "libmp3lame",
                "-qscale:a", "0", file_path
            ])
            print(saved_as)

            print("Writing metadata...")
            file = EasyID3(file_path)
            file["title"] = title
            file["artist"] = artist
            file["album"] = album
            file.save()
            file = ID3(file_path)

            if t.fetchAlbumCover(title, artist, album, "cover.jpg") != None:
                with open("cover.jpg", "rb") as albumArt:
                    file.add(
                        APIC(encoding=3,
                             mime='image/jpeg',
                             type=3,
                             desc=f"Cover of {title} — {artist}",
                             data=albumArt.read()))
                file.save()

            print("Metadata saved")

            try:
                os.remove("cover.jpg")
            except FileNotFoundError:
                pass

        if fileType == "flac":
            subprocess.run([
                "ffmpeg", "-y", "-i", wav_file, "-codec:a", "flac", file_path
            ])
            print(saved_as)

            print("Writing metadata...")
            file = FLAC(file_path)
            file["title"] = title
            file["artist"] = artist
            file["album"] = album

            if t.fetchAlbumCover(title, artist, album, "cover.jpg") != None:
                with open("cover.jpg", "rb") as albumArt:
                    art = Picture()
                    art.type = 3
                    art.mime = "image/jpeg"
                    art.desc = f"Cover of {title} — {artist}"
                    art.data = albumArt.read()
                    file.add_picture(art)
                file.save()

            print("Metadata saved")

        if fileType == "ogg":
            subprocess.run([
                "ffmpeg", "-y", "-i", wav_file, "-codec:a", "libvorbis",
                "-qscale:a", "10", file_path
            ])
            print(saved_as)

            print("Writing metadata...")
            file = OggVorbis(file_path)
            file["title"] = title
            file["artist"] = artist
            file["album"] = album
            file.save()

            print("Metadata saved")

        if fileType != "wav":
            os.remove(wav_file)

        try:
            os.remove("cover.jpg")
        except FileNotFoundError:
            pass


install_blackhole = """It seems like BlackHole isn't installed :( Please install it and try again.

https://github.com/ExistentialAudio/BlackHole

If it is installed then check if the name of the audio device is 'BlackHole 2ch' in Audio MIDI Setup and is being used as device output.

If you're not on a Mac device, please use the other version of this app"""


def check_blackhole() -> int:
    """
    Check if BlackHole is installed on the device.
    
    Returns: device_index if found, otherwise raises RuntimeError.
    """
    device_index = next((i for i, d in enumerate(sd.query_devices())
                         if "BlackHole" in d["name"]), None)
    if device_index is None:
        raise RuntimeError(install_blackhole)

    return device_index


def check_blackhole_selected() -> bool:
    """
    Check if BlackHole is selected as the output device.
    """
    output_devices = subprocess.check_output(
        ["SwitchAudioSource", "-t", "output", "-c"], text=True)
    return "BlackHole" in output_devices or "Multi-Output" in output_devices
