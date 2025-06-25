echo "MusRec - Dependency installer"
set -e
#checks if homebrew installed
if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Installing homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

#install other dependencies (switchaudio + ffmpeg) (ffmpreg lmao)
echo "Installing SwitchAudio and ffmpeg..."
brew install ffmpeg switchaudio-osx

#checks if blackhole is installed
if ! system_profiler SPAudioDataType | grep -q "BlackHole"; then
  echo "!! BlackHole not installed. Please install manually :( !!"
  echo "https://github.com/ExistentialAudio/BlackHole"
  echo "then rerun this installer"
  exit 1
fi

#venv
echo "Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

#python / pip dependencies
echo "Installing Python dependencies"
pip install --upgrade pip
pip install .

echo "Linking musrec to /usr/local/bin (you may need sudo)"
chmod +x .venv/bin/musrec
sudo ln -sf "$PWD/.venv/bin/musrec" /usr/local/bin/musrec

echo ""
echo "Installation finished!"