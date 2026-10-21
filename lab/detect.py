"""Detection: a deepfake classifier and the Perth watermark, before and after degradation."""

import numpy as np

from . import audio, state

CLASSIFIER_ID = "mo-thecreator/Deepfake-audio-detection"
# globals().get keeps loaded models when live_edit reloads this file after an edit.
CLASSIFIER = globals().get("CLASSIFIER")
WATERMARKER = globals().get("WATERMARKER")

VERSIONS = ("origineel", "mp3", "telefoon")


def load_classifier():
    global CLASSIFIER
    if CLASSIFIER is None:
        import torch
        from transformers import pipeline
        dev = 0 if torch.cuda.is_available() else -1
        CLASSIFIER = pipeline("audio-classification", model=CLASSIFIER_ID, device=dev)
    return CLASSIFIER


def load_watermarker():
    """The real Perth watermarker. perth silently sets the class to None if an import fails."""
    global WATERMARKER
    if WATERMARKER is None:
        import perth
        if perth.PerthImplicitWatermarker is None:
            raise RuntimeError("perth.PerthImplicitWatermarker is None (a perth import failed; check setuptools<81)")
        import torch
        WATERMARKER = perth.PerthImplicitWatermarker(device="cuda" if torch.cuda.is_available() else "cpu")
    return WATERMARKER


def unload():
    global CLASSIFIER, WATERMARKER
    CLASSIFIER = None
    WATERMARKER = None


def watermark_score(wav, sr):
    """Mean unrounded watermark prediction: about 1.0 for Chatterbox output, about 0.0 otherwise."""
    pred = load_watermarker().get_watermark(wav, sample_rate=sr, round=False)
    return float(np.mean(pred))


def fake_score(wav, sr):
    """Classifier's probability (0-1) that the clip is fake. The model expects 16 kHz."""
    import librosa
    wav16 = librosa.resample(wav, orig_sr=sr, target_sr=16000) if sr != 16000 else wav
    scores = load_classifier()({"raw": wav16, "sampling_rate": 16000}, top_k=None)
    return float(next(s["score"] for s in scores if s["label"].lower() == "fake"))


@state.requires_consent
def clips():
    """All real and cloned clips in data/, as (kind, path)."""
    found = [("echt", p) for p in sorted(state.subdir("real").glob("*.wav"))]
    found += [("kloon", p) for p in sorted(state.subdir("clones").glob("*.wav"))]
    return found


def degraded(path, version):
    """The clip as-is, after MP3 compression, or after a phone line (filters in audio.py)."""
    if version == "origineel":
        return path
    dst = state.subdir("degraded") / f"{path.stem}_{version}.wav"
    # Always re-run the filter, so edits to audio.mp3 / audio.phone_line take effect.
    return (audio.mp3 if version == "mp3" else audio.phone_line)(path, dst)


def summary(df):
    """Per kind and version: share the classifier got right and mean watermark score."""
    return (df.groupby(["soort", "versie"], sort=False)
              .agg(clips=("clip", "count"),
                   classifier_goed=("classifier_goed", "mean"),
                   watermerk_gem=("watermerk", "mean"))
              .round(2)
              .reset_index())
