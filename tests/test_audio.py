import numpy as np
import pytest
import soundfile as sf

from lab import audio
from conftest import speechlike

needs_ffmpeg = pytest.mark.skipif(audio.ffmpeg_bin() is None, reason="ffmpeg not available")


def test_speech_only_removes_silence():
    wav = np.concatenate([np.zeros(audio.SR), speechlike(5), np.zeros(2 * audio.SR)]).astype(np.float32)
    speech = audio.speech_only(wav)
    assert 3.0 < audio.duration(speech) < 5.5


def test_cut_and_normalize():
    wav = speechlike(12) * 0.05
    cut = audio.cut(wav, 3)
    assert audio.duration(cut) == pytest.approx(3.0)
    import pyloudnorm
    loud = pyloudnorm.Meter(audio.SR).integrated_loudness(audio.normalize_loudness(wav))
    assert loud == pytest.approx(audio.TARGET_LUFS, abs=1.0)


def test_prepare_for_test_resamples_to_24k(tmp_path):
    src = tmp_path / "in.wav"
    sf.write(src, speechlike(3, sr=48000), 48000)
    dst = audio.prepare_for_test(src, tmp_path / "out.wav")
    info = sf.info(dst)
    assert info.samplerate == audio.SR and info.subtype == "PCM_16" and info.channels == 1


@needs_ffmpeg
def test_phone_line_is_8k_and_band_limited(tmp_path):
    src = audio.save(tmp_path / "in.wav", speechlike(3))
    dst = audio.phone_line(src, tmp_path / "phone.wav")
    wav, sr = sf.read(dst)
    assert sr == 8000 and len(wav) == pytest.approx(3 * 8000, rel=0.05)


@needs_ffmpeg
def test_mp3_round_trip(tmp_path):
    src = audio.save(tmp_path / "in.wav", speechlike(3))
    wav, sr = sf.read(audio.mp3(src, tmp_path / "mp3.wav"))
    assert sr == audio.SR and len(wav) >= 3 * audio.SR * 0.95


@needs_ffmpeg
def test_decode_browser_recording(tmp_path):
    # Simulate a browser recording: encode to webm/opus with ffmpeg, then decode it back.
    src = audio.save(tmp_path / "in.wav", speechlike(2))
    webm = tmp_path / "rec.webm"
    audio._ffmpeg(["-i", str(src), "-c:a", "libopus", str(webm)])
    wav = audio.decode_bytes(webm.read_bytes())
    assert audio.duration(wav) == pytest.approx(2.0, abs=0.1)
