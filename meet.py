"""transcript-local: pornește cu `python meet.py`, oprește cu Ctrl+C.

Moduri:
  python meet.py                       meeting online: microfon + audio de sistem
  python meet.py --mic                 întâlnire fizică: doar microfonul
  python meet.py <mic.wav> <sys.wav>   re-transcriere din înregistrările salvate
  python meet.py <audio>               transcriere a unui singur fișier audio
"""
import datetime
import sys
import time
from pathlib import Path

from cleanup import CleanupError, clean_transcript
from merge import merge_segments, remove_echo, to_markdown
from transcribe import create_model, transcribe_wav

BASE = Path(__file__).parent
RECORDINGS = BASE / "recordings"
TRANSCRIPTS = BASE / "transcripts"


def _load_capture():
    """Modulul de captură depinde de sistemul de operare (vezi MAC.md)."""
    if sys.platform == "win32":
        import capture
        return capture
    if sys.platform == "darwin":
        try:
            import capture_mac
            return capture_mac
        except ImportError:
            print(
                "Pe macOS lipsește modulul de captură (capture_mac.py). "
                "Urmează pașii din MAC.md sau folosește MacWhisper și pune "
                "transcriptul în transcripts/."
            )
            sys.exit(1)
    print(f"Sistem de operare nesuportat pentru înregistrare: {sys.platform}")
    sys.exit(1)


def _finalize(merged, stamp, single_channel=False):
    """Scrie .raw.md, apoi încearcă curățarea Claude -> .md final."""
    md = to_markdown(merged, f"Meeting {stamp}")
    raw_path = TRANSCRIPTS / f"{stamp}.raw.md"
    raw_path.write_text(md, encoding="utf-8")
    out = TRANSCRIPTS / f"{stamp}.md"
    print("Curăț transcriptul cu Claude...")
    try:
        cleaned = clean_transcript(md, single_channel=single_channel)
        out.write_text(cleaned, encoding="utf-8")
        print(f"Gata. Transcript curățat: {out}")
    except CleanupError as e:
        out.write_text(md, encoding="utf-8")
        print(f"Curățarea Claude a eșuat ({e}); am păstrat varianta brută: {out}")


def transcribe_pair(mic_wav, sys_wav, stamp):
    print("Transcriu (10-20 min pentru 1h de meeting)...")
    model = create_model()
    others, lang = transcribe_wav(sys_wav, model)
    print(f"Limbă detectată: {lang}")
    mine, _ = transcribe_wav(mic_wav, model, language=lang)
    mine = remove_echo(mine, others)
    merged = merge_segments(mine, others)
    _finalize(merged, stamp)


def transcribe_single(audio_path, stamp):
    print("Transcriu (10-20 min pentru 1h de audio)...")
    model = create_model()
    segments, lang = transcribe_wav(audio_path, model)
    print(f"Limbă detectată: {lang}")
    merged = [(start, None, text) for start, text in segments]
    _finalize(merged, stamp, single_channel=True)


def _new_stamp(suffix_name):
    """Timestamp unic: două ședințe în același minut nu se suprascriu."""
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    suffix = 2
    while (RECORDINGS / f"{stamp}{suffix_name}").exists():
        stamp = f"{datetime.datetime.now().strftime('%Y-%m-%d-%H%M')}-{suffix}"
        suffix += 1
    return stamp


def _record_until_ctrl_c(recorder):
    started = time.time()
    print("Înregistrez. Apasă Ctrl+C la finalul meetingului.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    recorder.stop()
    minutes = int(time.time() - started) // 60
    print(f"\nÎnregistrare oprită ({minutes} min). Audio salvat în recordings/.")


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    RECORDINGS.mkdir(exist_ok=True)
    TRANSCRIPTS.mkdir(exist_ok=True)

    args = sys.argv[1:]

    if args == ["--mic"]:
        capture = _load_capture()
        stamp = _new_stamp("-mic.wav")
        mic_wav = RECORDINGS / f"{stamp}-mic.wav"
        print("Pornesc înregistrarea (doar microfon)...")
        _record_until_ctrl_c(capture.MicRecorder(mic_wav))
        transcribe_single(mic_wav, stamp)
        return

    if len(args) == 1:
        audio = Path(args[0])
        if not audio.exists():
            print(f"Nu găsesc fișierul: {audio}")
            sys.exit(1)
        transcribe_single(audio, audio.stem)
        return

    if len(args) == 2:
        mic_wav = Path(args[0])
        sys_wav = Path(args[1])
        for path in (mic_wav, sys_wav):
            if not path.exists():
                print(f"Nu găsesc fișierul: {path}")
                sys.exit(1)
        if mic_wav.name.endswith("-mic.wav"):
            stamp = mic_wav.name.removesuffix("-mic.wav")
        else:
            stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
        transcribe_pair(mic_wav, sys_wav, stamp)
        return

    if args:
        print(__doc__)
        sys.exit(1)

    capture = _load_capture()
    stamp = _new_stamp("-mic.wav")
    mic_wav = RECORDINGS / f"{stamp}-mic.wav"
    sys_wav = RECORDINGS / f"{stamp}-system.wav"
    print("Pornesc înregistrarea...")
    _record_until_ctrl_c(capture.DualRecorder(mic_wav, sys_wav))
    transcribe_pair(mic_wav, sys_wav, stamp)


if __name__ == "__main__":
    main()
