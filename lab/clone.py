"""Voice cloning with Chatterbox Multilingual. References come only from live recordings."""

import time
from pathlib import Path

from . import audio, state, texts
from .state import LabError

MODEL = None
MODEL_VERSION = None
_conditioned_on = None


def device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(dev=None):
    """Load Chatterbox Multilingual V3, falling back to V2 on releases without t3_model."""
    global MODEL, MODEL_VERSION
    if MODEL is not None:
        return MODEL
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    dev = dev or device()
    try:
        MODEL = ChatterboxMultilingualTTS.from_pretrained(device=dev, t3_model="v3")
        MODEL_VERSION = "v3"
    except TypeError:
        MODEL = ChatterboxMultilingualTTS.from_pretrained(device=dev)
        MODEL_VERSION = "v2"
    return MODEL


def unload():
    global MODEL, MODEL_VERSION, _conditioned_on
    MODEL = None
    MODEL_VERSION = None
    _conditioned_on = None


def reference_path(seconds):
    return state.subdir("ref") / f"ref_{seconds}s.wav"


def clone_path(sentence_id, seconds):
    return state.subdir("clones") / f"{sentence_id}_{seconds}s.wav"


@state.requires_consent
def make_references():
    """Cut the live reading recording into 3, 6 and 10 s of pure speech."""
    src = state.verified_recording("reference")
    speech = audio.speech_only(audio.load(src))
    if audio.duration(speech) < max(texts.REF_LENGTHS):
        raise LabError(f"Te weinig spraak in je opname ({audio.duration(speech):.1f} s). Neem de leestekst opnieuw op.")
    paths = {}
    for seconds in texts.REF_LENGTHS:
        path = audio.save(reference_path(seconds), audio.normalize_loudness(audio.cut(speech, seconds)))
        state.register_derived(path)
        paths[seconds] = path
    return paths


def _condition(ref):
    global _conditioned_on
    ref = Path(ref)
    if not ref.exists() or not state.is_verified(ref):
        # Own voice only: anything not cut from a live recording is refused.
        raise LabError("Klonen kan alleen met je eigen live opname uit stap 3.")
    if _conditioned_on != (ref, ref.stat().st_mtime_ns):
        MODEL.prepare_conditionals(str(ref), exaggeration=0.5)
        _conditioned_on = (ref, ref.stat().st_mtime_ns)


def _generate(text, lang, ref, dst):
    if MODEL is None:
        raise LabError("Het model is niet geladen. Voer eerst de setupcel (stap 1) uit.")
    _condition(ref)
    t0 = time.perf_counter()
    wav = MODEL.generate(text, language_id=lang).squeeze(0).cpu().numpy()
    elapsed = time.perf_counter() - t0
    audio.save(dst, wav, MODEL.sr)
    return {"audio_s": round(len(wav) / MODEL.sr, 1), "gen_s": round(elapsed, 1)}


@state.requires_consent
def run_experiment(progress=print):
    refs = make_references()
    results = []
    for seconds in texts.REF_LENGTHS:
        for s in texts.SENTENCES:
            progress(f"Bezig: {s['id']} met {seconds} s referentie...")
            dst = clone_path(s["id"], seconds)
            timing = _generate(s["text"], s["lang"], refs[seconds], dst)
            results.append({"zin": s["id"], "referentie_s": seconds, **timing,
                            "realtime_factor": round(timing["gen_s"] / max(timing["audio_s"], 0.1), 2),
                            "path": dst})
    return results


def check_free_text(text):
    text = (text or "").strip()
    if not text:
        raise LabError("Typ eerst een zin.")
    if len(text) > texts.FREE_MODE_MAX_CHARS:
        raise LabError(f"Maximaal {texts.FREE_MODE_MAX_CHARS} tekens.")
    hits = texts.blocked_terms(text)
    if hits:
        raise LabError("Deze tekst lijkt op een oplichtingsbericht (" + ", ".join(hits) + ") en wordt niet gegenereerd.")
    return text


@state.requires_consent
def generate_free(text, lang="nl", seconds=10):
    text = check_free_text(text)
    if lang not in ("nl", "en"):
        raise LabError("Kies Nederlands of Engels.")
    if seconds not in texts.REF_LENGTHS:
        raise LabError("Kies 3, 6 of 10 seconden.")
    ref = reference_path(seconds)
    if not ref.exists():
        make_references()
    n = len(list(state.subdir("clones").glob("vrij_*.wav"))) + 1
    dst = state.subdir("clones") / f"vrij_{n:02d}_{seconds}s.wav"
    timing = _generate(text, lang, ref, dst)
    return {"path": dst, **timing}
