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