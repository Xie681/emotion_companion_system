import sys

from modules.video_processor import extract_audio_from_video


def main() -> int:
    if len(sys.argv) != 3:
        print("用法：python -m modules.video_processor_worker <video_path> <output_dir>", file=sys.stderr)
        return 2

    try:
        audio_path = extract_audio_from_video(sys.argv[1], sys.argv[2])
        print(audio_path)
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
