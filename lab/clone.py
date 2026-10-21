"""Voice cloning with Chatterbox Multilingual: building blocks the notebook's step 4 and 5 use.

References come only from live recordings: condition() refuses anything else.
"""

from pathlib import Path

from . import audio, state, texts
from .state import LabError

# globals().get keeps the loaded model when autoreload re-runs this file after an edit.
MODEL = globals().get("MODEL")
MODEL_VERSION = globals().get("MODEL_VERSION")
VERSION = globals().get("VERSION", "v2")  # sounded best for Dutch in the dry run; setup can switch to "v3"
_conditioned_on = globals().get("_conditioned_on")


def device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(dev=None):
    """Load Chatterbox Multilingual (VERSION), falling back to V2 on releases without t3_model."""
    global MODEL, MODEL_VERSION
    if MODEL is not None and MODEL_VERSION == VERSION:
        return MODEL
    unload()
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    dev = dev or device()
    try:
        MODEL = ChatterboxMultilingualTTS.from_pretrained(device=dev, t3_model=VERSION)
        MODEL_VERSION = VERSION
    except TypeError:
        MODEL = ChatterboxMultilingualTTS.from_pretrained(device=dev)
        MODEL_VERSION = "v2"
    return MODEL


def require_model():
    if MODEL is None:
        raise LabError("Het model is niet geladen. Voer eerst de setupcel (stap 1) uit.")
    return MODEL


def unload():
    global MODEL, MODEL_VERSION, _conditioned_on
    MODEL = None
    MODEL_VERSION = None
    _conditioned_on = None


def reference_path(seconds):
    return state.subdir("ref") / f"ref_{seconds}s.wav"


def clone_path(name, seconds):
    return state.subdir("clones") / f"{name}_{seconds}s.wav"


@state.requires_consent
def load_reference_speech():
    """Your live reading recording from step 3a, with long pauses shortened."""
    return audio.compress_pauses(audio.load(state.verified_recording("reference")))


@state.requires_consent
def save_reference(speech, seconds):
    """Save the first `seconds` of speech as a reference clip and mark it as your own voice."""
    if audio.duration(speech) < seconds:
        raise LabError(f"Je opname bevat maar {audio.duration(speech):.1f} s spraak; neem de leestekst opnieuw op.")
    path = audio.save(reference_path(seconds), audio.normalize_loudness(audio.cut(speech, seconds, fade_s=0.02)))
    state.register_derived(path)
    return path


@state.requires_consent
def condition(ref):
    """Let the model 'listen' to a reference (model.prepare_conditionals), after checking it is your own voice."""
    global _conditioned_on
    model = require_model()
    ref = Path(ref)
    if not ref.exists() or not state.is_verified(ref):
        # Own voice only: anything not cut from a live recording is refused.
        raise LabError("Klonen kan alleen met je eigen live opname uit stap 3.")
    key = (ref, ref.stat().st_mtime_ns)
    if _conditioned_on != key:
        model.prepare_conditionals(str(ref))
        _conditioned_on = key


def to_numpy(wav):
    """Chatterbox returns a (1, samples) tensor; we store plain mono arrays."""
    return wav.squeeze(0).cpu().numpy() if hasattr(wav, "cpu") else wav


def save_clone(wav, name, seconds):
    return audio.save(clone_path(name, seconds), to_numpy(wav), require_model().sr)


def save_free(wav, seconds):
    n = len(list(state.subdir("clones").glob("vrij_*.wav"))) + 1
    return save_clone(wav, f"vrij_{n:02d}", seconds)


def check_free_text(text):
    """The free-mode scam filter: refuses empty, overlong or scam-like text (see texts.BLOCKLIST)."""
    text = (text or "").strip()
    if not text:
        raise LabError("Typ eerst een zin.")
    if len(text) > texts.FREE_MODE_MAX_CHARS:
        raise LabError(f"Maximaal {texts.FREE_MODE_MAX_CHARS} tekens.")
    hits = texts.blocked_terms(text)
    if hits:
        raise LabError("Deze tekst lijkt op een oplichtingsbericht (" + ", ".join(hits) + ") en wordt niet gegenereerd.")
    return text
