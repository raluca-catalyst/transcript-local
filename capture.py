"""Înregistrare pe Windows/WASAPI: microfon (eu) + audio de sistem (ceilalți).

Pe macOS acest fișier nu se folosește; vezi MAC.md (fișierul `capture_mac.py`
trebuie să ofere aceleași două clase: DualRecorder și MicRecorder).
"""
import threading
import wave

import pyaudiowpatch as pyaudio


def find_loopback_device(p):
    """Găsește dispozitivul de loopback al difuzoarelor default."""
    wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    try:
        speakers = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
    except (OSError, ValueError) as e:
        raise RuntimeError(
            "Nu există un dispozitiv de ieșire audio default în Windows. "
            "Setează unul înainte de a porni înregistrarea."
        ) from e
    if speakers.get("isLoopbackDevice"):
        return speakers
    for lb in p.get_loopback_device_info_generator():
        if speakers["name"] in lb["name"]:
            return lb
    raise RuntimeError(
        "Nu am găsit dispozitivul de loopback pentru difuzoare. "
        "Verifică output-ul audio default din Windows."
    )


class _ChannelRecorder:
    """Un stream de input scris continuu într-un WAV, prin callback."""

    def __init__(self, p, device_info, out_path):
        self.rate = int(device_info["defaultSampleRate"])
        self.channels = max(1, int(device_info["maxInputChannels"]))
        self._lock = threading.Lock()
        self._closed = False
        self._wav = wave.open(str(out_path), "wb")
        self._wav.setnchannels(self.channels)
        self._wav.setsampwidth(2)
        self._wav.setframerate(self.rate)
        self._stream = p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=device_info["index"],
            frames_per_buffer=1024,
            stream_callback=self._callback,
        )

    def _callback(self, in_data, frame_count, time_info, status):
        with self._lock:
            if not self._closed:
                self._wav.writeframes(in_data)
        return (None, pyaudio.paContinue)

    def close(self):
        self._stream.stop_stream()
        self._stream.close()
        with self._lock:
            self._closed = True
            self._wav.close()


class DualRecorder:
    """Pornește la construcție două înregistrări: microfon și loopback de sistem."""

    def __init__(self, mic_path, system_path):
        self.p = pyaudio.PyAudio()
        try:
            mic_info = self.p.get_default_input_device_info()
            loop_info = find_loopback_device(self.p)
            print(f"  Microfon: {mic_info['name']}")
            print(f"  Sistem:   {loop_info['name']}")
            self.mic = _ChannelRecorder(self.p, mic_info, mic_path)
            try:
                self.system = _ChannelRecorder(self.p, loop_info, system_path)
            except BaseException:
                self.mic.close()
                raise
        except BaseException:
            self.p.terminate()
            raise

    def stop(self):
        self.mic.close()
        self.system.close()
        self.p.terminate()


class MicRecorder:
    """Doar microfonul: pentru întâlniri fizice, unde microfonul prinde toată sala."""

    def __init__(self, mic_path):
        self.p = pyaudio.PyAudio()
        try:
            mic_info = self.p.get_default_input_device_info()
            print(f"  Microfon: {mic_info['name']}")
            self.mic = _ChannelRecorder(self.p, mic_info, mic_path)
        except BaseException:
            self.p.terminate()
            raise

    def stop(self):
        self.mic.close()
        self.p.terminate()
