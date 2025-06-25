import subprocess
import requests

def getService(service):
    if service == "spotify":
        return "Spotify"
    else:
        return "Music"

def getDuration(service):
    if service == "spotify":
        return float(subprocess.check_output([
            f"osascript", "-e", f"tell application \"Spotify\" to get duration of current track"
        ]).strip()) / 1000
    else:
        return float(subprocess.check_output([
            f"osascript", "-e", f"tell application \"Music\" to get duration of current track"
        ]).strip())


def getPosition(service):
    return float(subprocess.check_output([
        f"osascript", "-e", f"tell application \"{getService(service)}\" to get player position"
    ]).strip())


def setPlayerPos(position, service):
    subprocess.run([
        f"osascript", "-e", f"tell application \"{getService(service)}\" to set player position to {position}",
    ])

def pause(service):
    subprocess.run([
        f"osascript", "-e", f"tell application \"{getService(service)}\" to pause"
    ])

def play(service):
    subprocess.run([
        f"osascript", "-e", f"tell application \"{getService(service)}\" to play"
    ])

def getTitle(service):
    try:
        return subprocess.check_output([
            f"osascript", "-e", f"tell application \"{getService(service)}\" to get name of current track"
        ]).decode().strip()
    except:
        return None

def getArtist(service):
    try:
        return subprocess.check_output([
            f"osascript", "-e", f"tell application \"{getService(service)}\" to get artist of current track"
        ]).decode().strip()
    except:
        return None

def getAlbum(service):
    try:
        return subprocess.check_output([f"osascript", "-e", f"tell application \"{getService(service)}\"\nalbum of current track\nend tell"], text=True).strip()
    except subprocess.CalledProcessError:
        return None

def isPlaying(service):
    try:
        return True if subprocess.check_output([f"osascript", "-e", f"tell application \"{getService(service)}\" to get player state"]).decode().strip() == "playing" else False
    except subprocess.CalledProcessError:
        return False

def fetchAlbumCover(title, artist, album, saveAs="cover.jpg"):
    query = f"{title} {artist} {album}".replace(" ", "+")
    response = requests.get(f"https://itunes.apple.com/search?term={query}&limit=1&media=music")
    data = response.json()
    if data["resultCount"] == 0:
        print("No cover found")
        return None
    artworkUrl = data["results"][0]["artworkUrl100"].replace("100x100", "600x600")
    imgData = requests.get(artworkUrl).content
    with open(saveAs, "wb") as f:
        f.write(imgData)
    return saveAs

def adLikely(service): #idfk anymore i hate spotify so much why isn't this consistent
    #these are just red flags, idk... i'll prolly add a thing to skip ad-ignoring later :P
    if getTitle(service).strip() == "" or getArtist(service).strip() == "":
        return True
    elif getTitle(service).strip() == "" and getArtist(service).strip().lower() in ["advertisement", "spotify"] or getArtist(service).strip() == "" and getTitle(service).strip().lower() in ["advertisement", "spotify"]:
        return True
    elif getAlbum(service).strip() == "" and getTitle(service).strip() == "" and getDuration() <= 30:
        return True
    else:
        return False

play("apple-music")
print(getDuration("apple-music"))