import argparse
from musrec.recorder import recorder
from musrec.config import *

def main():
    parser = argparse.ArgumentParser(description='Records music and exports them to audio files automatically.')
    subparsers = parser.add_subparsers(dest='command', required=False)

    #record
    recParser = subparsers.add_parser('record', help='Records music and exports them to audio files automatically.')
    recParser.add_argument(
        "--format", "-f", choices = ["wav", "mp3", "flac", "ogg", "m4a"], default=load()["outputFormat"], help=f"Output file format; (default: .{load()["outputFormat"]}) (supported: .wav (automatic metadata not supported), .mp3, .flac, .ogg (no album art), .m4a (ALAC))."
    )
    recParser.add_argument(
        "--trackcount", "-tc", default=load()["trackCount"], type=int, help=f"Number of tracks to record (default: {load()["trackCount"]})."
    )
    recParser.add_argument(
        "--samplerate", "-sr", default=load()["sampleRate"], type=int, help=f"Sampling rate (default: {load()["sampleRate"]})."
    )
    recParser.add_argument(
        "--channels", "-c", default=load()["channels"], type=int, help=f"Number of audio channels (default: {load()["channels"]})."
    )
    recParser.add_argument(
        "--blocksize", "-b", default=load()["blockSize"], type=int, help=f"Block size (default: {load()["blockSize"]})."
    )
    recParser.add_argument(
        "--force", "-fr", default=False, action="store_true", help="Skip warnings (default: False)."
    )
    recParser.add_argument(
        "--outputdir", "-o", default=load()["outputDir"], help=f"Output directory (default: {load()["outputDir"]})."
    )
    recParser.add_argument(
        "--disableadskip", "-da", default=bool(load()["adSkip"]), action="store_false", help=f"Disables skipping recording ads (default: {load()["adSkip"]} - 0: false, 1: true)."
    )
    recParser.add_argument(
        "--service", "-s", choices=["spotify", "apple-music"], default=load()["service"], help=f"Streaming service used (default: {load()["service"]})."
    )
    recParser.add_argument(
        "--bitrate", "-br", choices=["32k", "64k", "96k", "128k", "160k", "192k", "224k", "256k", "320k"], default=load()["bitrate"], help=f"MP3 export bitrate (default: {load()["bitrate"]})."
    )

    #config
    confParser = subparsers.add_parser('config', help='Configure default settings.')
    confParser.add_argument("--set", nargs=2, metavar=("key","value"), help="Set config value (format: key=value).")
    confParser.add_argument("--reset", default=False, action="store_true", help="Reset config to default settings.")
    confParser.add_argument("--show", default=False, action="store_true", help="Show current configuration.")


    args = parser.parse_args()

    if args.command == 'config':
        if args.reset:
            reset()
        if args.set:
            key, value = args.set
            current = load()
            if key in current:
                try:
                    castValue = type(defaultConfig[key])(value)
                    current[key] = castValue
                    save(current)
                    print(f"{key} set to {castValue}")
                except ValueError:
                    print(f"Unknown value type for {key}.")
            else:
                print(f"Unkown key {key}.")
        if args.show:
            print(load())
        if not (args.set or args.reset or args.show):
            confParser.print_help()
            return


    else:
        recorder(
            args.trackcount,
            args.format,
            args.samplerate,
            args.channels,
            args.blocksize,
            args.force,
            args.outputdir,
            args.disableadskip,
            args.service,
            args.bitrate
        )

if __name__ == '__main__':
    main()