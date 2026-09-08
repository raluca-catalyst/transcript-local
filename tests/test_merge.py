from config import MY_LABEL, OTHERS_LABEL
from merge import merge_segments, format_timestamp, to_markdown, remove_echo


def test_merge_interleaves_by_time():
    mine = [(0.0, "Bună, ce faceți?"), (10.0, "Perfect.")]
    others = [(5.0, "Bine, mulțumim.")]
    result = merge_segments(mine, others)
    assert result == [
        (0.0, MY_LABEL, "Bună, ce faceți?"),
        (5.0, OTHERS_LABEL, "Bine, mulțumim."),
        (10.0, MY_LABEL, "Perfect."),
    ]


def test_merge_joins_consecutive_same_speaker():
    mine = [(0.0, "Prima frază."), (3.0, "A doua frază.")]
    others = [(20.0, "Răspuns.")]
    result = merge_segments(mine, others)
    assert result == [
        (0.0, MY_LABEL, "Prima frază. A doua frază."),
        (20.0, OTHERS_LABEL, "Răspuns."),
    ]


def test_merge_empty_others():
    result = merge_segments([(1.0, "Monolog.")], [])
    assert result == [(1.0, MY_LABEL, "Monolog.")]


def test_format_timestamp():
    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(75.9) == "00:01:15"
    assert format_timestamp(3661) == "01:01:01"


def test_to_markdown():
    merged = [(0.0, MY_LABEL, "Salut."), (65.0, OTHERS_LABEL, "Salut și ție.")]
    md = to_markdown(merged, "Meeting 2026-07-06-1400")
    assert md.startswith("# Meeting 2026-07-06-1400\n")
    assert f"**[00:00:00] {MY_LABEL}:** Salut." in md
    assert f"**[00:01:05] {OTHERS_LABEL}:** Salut și ție." in md


def test_remove_echo_drops_garbled_duplicate():
    # ecoul boxelor apare stâlcit pe canalul mic
    others = [(57.0, "Dar e o perioadă foarte aglomerată, suntem...")]
    mine = [(57.5, "Dar e o perioada foarte aglomerata, suntem")]
    assert remove_echo(mine, others) == []


def test_remove_echo_keeps_real_interjection():
    others = [(10.0, "Toată lumea s-a speriat de picul din iunie.")]
    mine = [(10.5, "Da, exact, și noi am simțit asta.")]
    assert remove_echo(mine, others) == mine


def test_remove_echo_ignores_far_apart_similar_text():
    # text identic dar la 30s distanță = repetiție reală, nu ecou
    others = [(5.0, "E o perioadă aglomerată.")]
    mine = [(35.0, "E o perioadă aglomerată.")]
    assert remove_echo(mine, others) == mine


def test_to_markdown_unlabeled():
    md = to_markdown([(65.0, None, "Text dintr-o înregistrare cu un singur canal.")], "Meeting X")
    assert "**[00:01:05]** Text dintr-o înregistrare cu un singur canal." in md
