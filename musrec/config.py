import json, os
configPath = "./config/config.json"

defaultConfig = {
    "outputFormat":"wav",
    "sampleRate":16000,
    "channels":2,
    "blockSize":1024,
    "adSkip":True,
    "outputDir":".",
    "trackCount":10,
    "service":"spotify",
    "bitrate":"320k"
}

def checkDir():
    os.makedirs(os.path.dirname(configPath), exist_ok=True)

def load():
    try:
        checkDir()
        with open(configPath,"r") as f:
            return {**defaultConfig, **json.loads(f)}
    except FileNotFoundError:
        return defaultConfig

def save(config):
    try:
        checkDir()
        with open(configPath, "w") as f:
            json.dump(config, f, indent=2)
    except FileNotFoundError:
        print(f"{configPath} not found.")

def reset():
    try:
        checkDir()
        with open(configPath,"w") as f:
            json.dump(defaultConfig, f)
    except FileNotFoundError:
        pass
