import argparse
from recorder import recorder

def main():
    parser = argparse.ArgumentParser(description='Records music and exports them to audio files automatically.')
    parser.add_argument(
        "--format", "-f", choices = ["wav", "mp3", "flac"], default="wav", help="Output file format; (default: .wav) (supported: .wav (automatic ID3 metadata not supported), .mp3, .flac)."
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
        "--skipwarning", "-sw", default=False, action="store_true", help="Skip warnings (default: False)."
    )
    parser.add_argument(
        "--outputdir", "-o", default=".", help="Output directory (default: .)."
    )

    args = parser.parse_args()
    recorder(
        args.trackcount,
        args.format,
        args.samplerate,
        args.channels,
        args.blocksize,
        args.skipwarning,
        args.outputdir
    )



if __name__ == '__main__':
    main()