import pytest

from cleanup import PROMPT, PROMPT_SINGLE, CleanupError, clean_transcript, _chunk_lines
from config import MY_LABEL, OTHERS_LABEL


def _fake_run(prompt, chunk):
    return chunk.replace("aglomerata", "aglomerată")


def _multi_chunk_text(n=150, title=None):
    lines = [title, ""] if title else []
    for i in range(n):
        lines.append(f"**[00:00:{i:02d}] {MY_LABEL}:** linia {i}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def test_prompt_uses_labels_from_config():
    assert MY_LABEL in PROMPT and OTHERS_LABEL in PROMPT
    assert "{me}" not in PROMPT and "{others}" not in PROMPT


def test_chunk_splits_on_blank_lines():
    text = "\n".join(f"**[00:00:{i:02d}] {MY_LABEL}:** linia {i}\n" for i in range(100))
    chunks = _chunk_lines(text.splitlines(), max_lines=50)
    assert len(chunks) >= 2
    for c in chunks[:-1]:
        assert c[-1] == ""  # tăiem doar la linie goală
    assert sum(len(c) for c in chunks) == len(text.splitlines())


def test_clean_transcript_applies_run_to_all_chunks():
    text = f"# Meeting X\n\n**[00:00:01] {MY_LABEL}:** perioada aglomerata\n"
    out = clean_transcript(text, run=_fake_run)
    assert "aglomerată" in out
    assert out.startswith("# Meeting X")


def test_clean_transcript_preserves_blank_lines_between_chunks():
    text = _multi_chunk_text()
    out = clean_transcript(text, run=lambda prompt, chunk: chunk)
    assert out == text
    out_lines = out.splitlines()
    for i in range(0, len(out_lines) - 1, 2):
        assert out_lines[i].startswith("**[")
        assert out_lines[i + 1] == ""


def test_clean_transcript_falls_back_per_chunk_on_double_failure(capsys):
    def flaky(prompt, chunk):
        if chunk.startswith("**[00:00:00]"):
            raise RuntimeError("claude indisponibil")
        return chunk.replace("linia", "rândul")

    out = clean_transcript(_multi_chunk_text(), run=flaky)
    assert "linia 0" in out  # bucata eșuată a rămas brută
    assert "rândul 149" in out  # celelalte bucăți au fost curățate
    assert "necurățate" in capsys.readouterr().out


def test_clean_transcript_retries_once_then_succeeds():
    calls = {"n": 0}

    def flaky_once(prompt, chunk):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("timeout tranzitoriu")
        return chunk.replace("aglomerata", "aglomerată")

    out = clean_transcript(f"**[00:00:01] {MY_LABEL}:** perioada aglomerata\n", run=flaky_once)
    assert "aglomerată" in out
    assert calls["n"] == 2


def test_clean_transcript_keeps_title_even_if_model_drops_it():
    def drops_first_line(prompt, chunk):
        rest = "\n".join(chunk.splitlines()[1:]).lstrip("\n")
        return rest.replace("aglomerata", "aglomerată")

    text = (
        "# Meeting 2026-07-22-1106\n\n"
        f"**[00:00:01] {MY_LABEL}:** prima replica\n\n"
        f"**[00:00:05] {OTHERS_LABEL}:** perioada aglomerata\n"
    )
    out = clean_transcript(text, run=drops_first_line)
    assert out == (
        "# Meeting 2026-07-22-1106\n\n"
        f"**[00:00:05] {OTHERS_LABEL}:** perioada aglomerată\n"
    )


def test_clean_transcript_title_survives_across_multiple_chunks():
    text = _multi_chunk_text(title="# Meeting 2026-07-22-1106")
    out = clean_transcript(text, run=lambda prompt, chunk: chunk)
    assert out == text


def test_clean_transcript_single_channel_uses_prompt_without_attribution():
    prompts = []

    def identity(prompt, chunk):
        prompts.append(prompt)
        return chunk

    text = (
        "# Meeting 2026-07-31-2050\n\n"
        "**[00:00:00]** perioada aglomerata\n\n"
        "**[00:00:07]** da, exact\n"
    )
    out = clean_transcript(text, run=identity, single_channel=True)
    assert out == text
    assert prompts and all(p == PROMPT_SINGLE for p in prompts)
    assert OTHERS_LABEL not in PROMPT_SINGLE and MY_LABEL not in PROMPT_SINGLE


def test_clean_transcript_default_keeps_two_channel_prompt():
    prompts = []
    clean_transcript(
        f"**[00:00:01] {MY_LABEL}:** ceva\n",
        run=lambda p, c: prompts.append(p) or c,
    )
    assert prompts == [PROMPT]


def test_clean_transcript_raises_when_all_chunks_fail():
    def boom(prompt, chunk):
        raise RuntimeError("claude indisponibil")

    with pytest.raises(CleanupError):
        clean_transcript(f"**[00:00:01] {MY_LABEL}:** ceva\n", run=boom)
    with pytest.raises(CleanupError):
        clean_transcript(_multi_chunk_text(), run=boom)
