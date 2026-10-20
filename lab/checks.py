"""Setup checks with one Dutch pass/fail line each."""

import time

import numpy as np

from . import audio, clone, detect

TEST_TEXT = "Hallo allemaal, de test werkt."


def _gpu():
    import torch
    if torch.cuda.is_available():
        return True, f"GPU gevonden: {torch.cuda.get_device_name(0)}"
    return False, ("Geen GPU. Kies Runtime → Runtimetype wijzigen → T4 GPU en voer deze cel opnieuw uit. "
                   "Lukt dat niet, werk dan samen op de runtime van je partner.")


def _ffmpeg():
    exe = audio.ffmpeg_bin()
    return (True, "ffmpeg gevonden") if exe else (False, "ffmpeg ontbreekt")


def _perth():
    try:
        detect.load_watermarker()
        return True, "Watermerk-detector (Perth) geladen"
    except Exception as e:
        return False, f"Watermerk-detector werkt niet: {e}"


def _chatterbox():
    t0 = time.perf_counter()
    try:
        clone.load_model()
        return True, f"Kloonmodel Chatterbox {clone.MODEL_VERSION} geladen ({time.perf_counter() - t0:.0f} s)"
    except Exception as e:
        return False, f"Kloonmodel laden mislukt: {e}"


def _classifier():
    try:
        detect.load_classifier()
        return True, "Deepfake-classifier geladen"
    except Exception as e:
        return False, f"Classifier laden mislukt (de rest werkt wel): {e}"


def _test_generation():
    if clone.MODEL is None:
        return False, "Testgeneratie overgeslagen: model niet geladen"
    t0 = time.perf_counter()
    wav = clone.MODEL.generate(TEST_TEXT, language_id="nl").squeeze(0).cpu().numpy()
    elapsed = time.perf_counter() - t0
    if len(wav) < clone.MODEL.sr * 0.5 or not np.isfinite(wav).all():
        return False, "Testgeneratie gaf geen bruikbare audio"
    if detect.WATERMARKER is None:
        return True, f"Testzin gegenereerd in {elapsed:.1f} s (watermerk niet gecontroleerd)"
    score = detect.watermark_score(wav, clone.MODEL.sr)
    if score < 0.5:
        return False, f"Testzin gegenereerd, maar watermerk is {score:.2f} (verwacht ~1.0)"
    return True, f"Testzin gegenereerd in {elapsed:.1f} s, watermerk {score:.2f}"


CHECKS = [_gpu, _ffmpeg, _perth, _chatterbox, _classifier, _test_generation]


def run(report=print):
    results = []
    for check in CHECKS:
        try:
            ok, message = check()
        except Exception as e:
            ok, message = False, f"{check.__name__.strip('_')}: {e}"
        report(("✅ " if ok else "❌ ") + message)
        results.append((check.__name__.strip("_"), ok, message))
    return results
