from transcribe import transcribe_wav


class _FakeInfo:
    def __init__(self, language):
        self.language = language


class _FakeSegment:
    def __init__(self, start, text):
        self.start = start
        self.text = text


class _FakeModel:
    """Simulează faster-whisper: prima detecție cade pe o limbă nesuportată."""

    def __init__(self, first_language="pt"):
        self.calls = []
        self.first_language = first_language

    def transcribe(self, path, language=None, **kwargs):
        self.calls.append(language)
        if language is None:
            return iter([_FakeSegment(0.0, "texto de exemplo")]), _FakeInfo(self.first_language)
        return iter([_FakeSegment(0.0, "text în română"), _FakeSegment(2.0, "  ")]), _FakeInfo(language)


def test_transcribe_clamps_unsupported_language_to_ro():
    fake_model = _FakeModel(first_language="pt")
    segments, lang = transcribe_wav("fake.wav", fake_model)
    assert lang == "ro"
    assert fake_model.calls == [None, "ro"]
    assert segments == [(0.0, "text în română")]  # segmentele goale se ignoră


def test_transcribe_keeps_locked_language():
    fake_model = _FakeModel()
    segments, lang = transcribe_wav("fake.wav", fake_model, language="en")
    assert lang == "en"
    assert fake_model.calls == ["en"]
