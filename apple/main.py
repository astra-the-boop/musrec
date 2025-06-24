import argparse
from recorder import recorder

def main():
    parser = argparse.ArgumentParser(description='Records music and exports them to audio files automatically.')
    parser.add_argument(
        "--format", "-f", choices = ["wav", "mp3", "flac", "ogg"], default="wav", help="Output file format; (default: .wav) (supported: .wav (automatic ID3 metadata not supported), .mp3, .flac, .ogg (no album art))."
    )
    parser.add_argument(
        "--trackcount", "-tc", default=10, type=int, help="Number of tracks to record (default: 10)."
    )
    parser.add_argument(
        "--samplerate", "-sr", default=44100, type=int, help="Sampling rate (default: 44100)."
    )
    parser.add_argument(
        "--channels", "-c", default=2, type=int, help="Number of audio channels (default: 2)."
    )
    parser.add_argument(
        "--blocksize", "-b", default=1024, type=int, help="Block size (default: 1024)."
    )
    parser.add_argument(
        "--force", "-fr", default=False, action="store_true", help="Skip warnings (default: False)."
    )
    parser.add_argument(
        "--outputdir", "-o", default=".", help="Output directory (default: .)."
    )
    parser.add_argument(
        "--disableadskip", "-da", default=True, action="store_false", help="Disables skipping recording ads (default: False)."
    )

    args = parser.parse_args()
    recorder(
        args.trackcount,
        args.format,
        args.samplerate,
        args.channels,
        args.blocksize,
        args.force,
        args.outputdir,
        args.disableadskip
    )



if __name__ == '__main__':
    main()