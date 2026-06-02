import sys

from modules.speech_to_text import transcribe_audio


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：python -m modules.speech_to_text_worker <audio_path>", file=sys.stderr)
        return 2

    try:
        print(transcribe_audio(sys.argv[1]))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
