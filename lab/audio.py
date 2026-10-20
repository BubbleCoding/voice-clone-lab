"""Audio helpers: decode, trim, loudness-normalize, cut, and the phone-line and MP3 filters."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000  # Chatterbox output rate; all lab audio is stored at this rate
TARGET_LUFS = -23.0


def ffmpeg_bin():
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def _ffmpeg(args, input_bytes=None):
    exe = ffmpeg_bin()
    if exe is None:
        raise RuntimeError("ffmpeg not found")
    result = subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-y", *args],
                            input=input_bytes, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode(errors='replace')[:500]}")
    return result.stdout


def decode_bytes(data, sr=SR):
    """Decode any browser recording (webm/opus, mp4/aac, wav) to a mono float32 array."""
    raw = _ffmpeg(["-i", "pipe:0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "pipe:1"], input_bytes=data)
    return np.frombuffer(raw, dtype=np.float32).copy()


def load_native(path):
    """Mono float32 at the file's own sample rate, as (wav, sr)."""
    wav, file_sr = sf.read(str(path), dtype="float32", always_2d=False)
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    return wav, file_sr


def load(path, sr=SR):
    wav, file_sr = load_native(path)
    if file_sr != sr:
        import librosa
        wav = librosa.resample(wav, orig_sr=file_sr, target_sr=sr)
    return wav.astype(np.float32)


def save(path, wav, sr=SR):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.clip(wav, -1.0, 1.0), sr, subtype="PCM_16")
    return Path(path)


def duration(wav, sr=SR):
    return len(wav) / sr


def trim(wav, top_db=40):
    """Remove leading and trailing silence."""
    import librosa
    if len(wav) == 0:
        return wav
    trimmed, _ = librosa.effects.trim(wav, top_db=top_db)
    return trimmed


def speech_only(wav, sr=SR, top_db=40, gap_s=0.15):
    """Keep only voiced parts, joined by short gaps, so '3 s of reference' means 3 s of speech."""
    import librosa
    intervals = librosa.effects.split(wav, top_db=top_db)
    if len(intervals) == 0:
        return np.zeros(0, dtype=np.float32)
    gap = np.zeros(int(gap_s * sr), dtype=np.float32)
    parts = []
    for start, end in intervals:
        if end - start < int(0.05 * sr):
            continue  # clicks and breaths
        parts.extend([wav[start:end], gap])
    return np.concatenate(parts[:-1]) if parts else np.zeros(0, dtype=np.float32)


def normalize_loudness(wav, sr=SR, target=TARGET_LUFS):
    """Normalize to target LUFS, keeping the peak below -1 dBFS."""
    import pyloudnorm
    if duration(wav, sr) < 0.5 or not np.any(wav):
        return wav
    meter = pyloudnorm.Meter(sr)
    loudness = meter.integrated_loudness(wav)
    if not np.isfinite(loudness):
        return wav
    out = pyloudnorm.normalize.loudness(wav, loudness, target)
    peak = np.max(np.abs(out))
    limit = 10 ** (-1 / 20)
    if peak > limit:
        out = out * (limit / peak)
    return out.astype(np.float32)


def cut(wav, seconds, sr=SR):
    return wav[: int(seconds * sr)]


def prepare_for_test(src, dst):
    """Same rate, trimming and loudness for every listening-test clip, so format gives nothing away."""
    wav = normalize_loudness(trim(load(src)))
    return save(dst, wav)


def phone_line(src, dst, noise_dbfs=-35.0, seed=0):
    """8 kHz mono, 300-3400 Hz band-pass, G.711 mu-law round trip, light white noise."""
    with tempfile.TemporaryDirectory() as tmp:
        mulaw = Path(tmp) / "line.wav"
        _ffmpeg(["-i", str(src), "-ac", "1", "-ar", "8000",
                 "-af", "highpass=f=300,lowpass=f=3400", "-c:a", "pcm_mulaw", str(mulaw)])
        decoded = Path(tmp) / "decoded.wav"
        _ffmpeg(["-i", str(mulaw), "-c:a", "pcm_s16le", str(decoded)])
        wav, sr = sf.read(str(decoded), dtype="float32")
    rng = np.random.default_rng(seed)
    wav = wav + rng.standard_normal(len(wav)).astype(np.float32) * (10 ** (noise_dbfs / 20))
    return save(dst, wav, sr)


def mp3(src, dst, bitrate="128k"):
    with tempfile.TemporaryDirectory() as tmp:
        encoded = Path(tmp) / "clip.mp3"
        _ffmpeg(["-i", str(src), "-c:a", "libmp3lame", "-b:a", bitrate, str(encoded)])
        _ffmpeg(["-i", str(encoded), "-c:a", "pcm_s16le", str(dst)])
    return Path(dst)
