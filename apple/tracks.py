import subprocess
import requests

def getDuration():
    return float(subprocess.check_output([
        "osascript", "-e", "tell application \"Spotify\" to get duration of current track"
    ]).strip())/1000

def getPosition():
    return float(subprocess.check_output([
        "osascript", "-e", "tell application \"Spotify\" to get player position"
    ]).strip())


def setPlayerPos(position):
    subprocess.run([
        "osascript", "-e", f"tell application \"Spotify\" to set player position to {position}",
    ])

def pause():
    subprocess.run([
        "osascript", "-e", "tell application \"Spotify\" to pause"
    ])

def play():
    subprocess.run([
        "osascript", "-e", "tell application \"Spotify\" to play"
    ])

def getTitle():
    try:
        return subprocess.check_output([
            "osascript", "-e", "tell application \"Spotify\" to get name of current track"
        ]).decode().strip()
    except:
        return None

def getArtist():
    try:
        return subprocess.check_output([
            "osascript", "-e", "tell application \"Spotify\" to get artist of current track"
        ]).decode().strip()
    except:
        return None

def getAlbum():
    try:
        return subprocess.check_output(["osascript", "-e", "tell application \"Spotify\"\nalbum of current track\nend tell"], text=True).strip()
    except subprocess.CalledProcessError:
        return None

def isPlaying():
    try:
        return True if subprocess.check_output(["osascript", "-e", "tell application \"Spotify\" to get player state"]).decode().strip() == "playing" else False
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

def adLikely(): #idfk anymore i hate spotify so much why isn't this consistent
    #these are just red flags, idk... i'll prolly add a thing to skip ad-ignoring later :P
    if getTitle().strip() == "" or getArtist().strip() == "":
        return True
    elif getTitle().strip() == "" and getArtist().strip().lower() in ["advertisement", "spotify"] or getArtist().strip() == "" and getTitle().strip().lower() in ["advertisement", "spotify"]:
        return True
    elif getAlbum().strip() == "" and getTitle().strip() == "" and getDuration() <= 30:
        return True
    else:
        return False