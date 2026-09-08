"""Împletește transcripturile celor două canale într-un dialog markdown."""

import difflib
import unicodedata

from config import MY_LABEL, OTHERS_LABEL

ECHO_WINDOW = 2.0
ECHO_THRESHOLD = 0.6


def _normalize(text):
    """lowercase, fără diacritice, fără punctuație — pentru comparat ecouri."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if c.isalnum() or c.isspace()).strip()


def remove_echo(mine, others, window=ECHO_WINDOW, threshold=ECHO_THRESHOLD):
    """Elimină din `mine` segmentele care sunt ecou al boxelor (dubluri ale `others`)."""
    kept = []
    for start, text in mine:
        norm = _normalize(text)
        is_echo = False
        for o_start, o_text in others:
            if abs(o_start - start) > window:
                continue
            ratio = difflib.SequenceMatcher(None, norm, _normalize(o_text)).ratio()
            if ratio >= threshold:
                is_echo = True
                break
        if not is_echo:
            kept.append((start, text))
    return kept


def merge_segments(mine, others):
    """(start, text) pe două canale -> listă sortată (start, label, text).

    Replicile consecutive ale aceluiași vorbitor se unesc într-un singur paragraf.
    """
    tagged = [(s, MY_LABEL, t) for s, t in mine] + [
        (s, OTHERS_LABEL, t) for s, t in others
    ]
    tagged.sort(key=lambda x: x[0])
    merged = []
    for start, label, text in tagged:
        if merged and merged[-1][1] == label:
            prev_start, _, prev_text = merged[-1]
            merged[-1] = (prev_start, label, prev_text + " " + text)
        else:
            merged.append((start, label, text))
    return merged


def format_timestamp(seconds):
    s = int(seconds)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def to_markdown(merged, title):
    lines = [f"# {title}", ""]
    for start, label, text in merged:
        if label:
            lines.append(f"**[{format_timestamp(start)}] {label}:** {text}")
        else:
            lines.append(f"**[{format_timestamp(start)}]** {text}")
        lines.append("")
    return "\n".join(lines)
