import subprocess

def getDuration():
    results = subprocess.check_output([
        "osascript", "-e", "tell application \"Spotify\" to get duration of current track"
    ])
    return float(results.strip())/1000

def getPosition():
    results = subprocess.check_output([
        "osascript", "-e", "tell application \"Spotify\" to get player position"
    ])
    return float(results.strip())

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