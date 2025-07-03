#requires Blackhole installed and set up with 2 channels because tim apple is a bitch
#https://github.com/ExistentialAudio/BlackHole
#also ffmpeg too
#recorder.py
#thankyu tobycm for refactoring my spaghetti ahh code :wilted flower emoji:
import os
import subprocess
import sys
import shutil
from time import sleep, time

import numpy as np
import sounddevice as sd
import soundfile as sf
import musrec.tracks as t
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover


def recorder(track_count,
             fileType="wav",
             sample_rate=44100,
             channels=2,
             blocksize=1024,
             skipWarning=False,
             outputDir=".",
             adSkip=True,
             service="spotify",
             bitrate="320k"):
    os.makedirs(outputDir, exist_ok=True)

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recordedChunks.append(indata.copy())

    if not skipWarning:
        #checks if external (non-python) dependencies / apps are presents :(
        if sys.platform != 'darwin':
            raise RuntimeError('!! MusRec currently only supports MacOS !!')
        if not shutil.which('ffmpeg'):
            sys.exit(1) if input("Missing: ffmpeg; ffmpeg is required for .mp3, .flac, .ogg exports\n\nPlease install it via Homebrew:\nbrew install ffmpeg\n\nEnter [c] to cancel; enter anything else to proceed") == "c" else None
        if not shutil.which('SwitchAudioSource'):
            sys.exit(1) if input("Missing: SwitchAudioSource; SwitchAudioSource is required to detect current output device\n\nPlease install it via Homebrew:\nbrew install switchaudio-osx\n\nEnter [c] to cancel; enter anything else to proceed") == "c" else None

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
        t.pause(service)
        duration = t.getDuration(service)
        if t.getPosition(service) != 0:
            t.setPlayerPos(0, service)
        title = t.getTitle(service)
        artist = t.getArtist(service)
        album = t.getAlbum(service)

        while t.adLikely(service) and adSkip:
            t.play(service)
            print("Advertisement likely, skipping recording for track")
            sleep(t.getDuration(service))

        recordedChunks = []
        t.play(service)

        print(
            f"({i}/{track_count}) Currently recording {title} by {artist} with length of {t.getDuration(service)} seconds; Pause music to stop recording"
        )

        with sd.InputStream(samplerate=sample_rate,
                            channels=channels,
                            callback=callback,
                            blocksize=blocksize,
                            device=device_index,
                            dtype='float32'):
            start_time = time()
            sleep(1)
            while t.isPlaying(service) and (time() - start_time) < duration:
                sleep(0.1)
            print("Recording stopped")

        interrupted = not t.isPlaying(service) and (time() - start_time) < duration

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
                "-b:a", bitrate, file_path
            ],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
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
            ],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
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
            ],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(saved_as)

            print("Writing metadata...")
            file = OggVorbis(file_path)
            file["title"] = title
            file["artist"] = artist
            file["album"] = album
            file.save()

            print("Metadata saved")

        if fileType == "m4a":
            subprocess.run([
                "ffmpeg", "-y", "-i", wav_file, "-c:a", "alac", file_path
            ],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(saved_as)
            print("Writing metadata...")
            file = MP4(file_path)
            file["\xa9nam"] = title
            file["\xa9ART"] = artist
            file["\xa9alb"] = album

            if t.fetchAlbumCover(title, artist, album, "cover.jpg") != None:
                with open("cover.jpg", "rb") as albumArt:
                    file["covr"] = [MP4Cover(albumArt.read(),imageformat=MP4Cover.FORMAT_JPEG)]

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

If it is installed then check if the name of the audio device is 'BlackHole 2ch' in Audio MIDI Setup and is being used as device output."""


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
    #Check if BlackHole is selected as the output device.
    try:
        output_devices = subprocess.check_output(
            ["SwitchAudioSource", "-t", "output", "-c"], text=True)
        return "BlackHole" in output_devices or "Multi-Output" in output_devices
    except (subprocess.CalledProcessError, FileNotFoundError):
        return True if input("Warning: SwitchAudioSource not found, please check manually if BlackHole is currently being used as audio output in System Settings > Sound > Output; Enter [c] to cancel")!="c" else sys.exit(1)