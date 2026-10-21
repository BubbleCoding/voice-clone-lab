"""Step 5, Echt of nep?: the real test sentence and its clones, shuffled, for a partner to guess."""

import random
import re

from . import audio, state, texts
from .state import LabError

_CLONE_RE = re.compile(rf"^{texts.TARGET_ID}_(\d+)s\.wav$")


def _clones():
    """(seconds, path) for every clone of the test sentence, whatever REF_LENGTHS step 4 used."""
    found = []
    for path in state.subdir("clones").glob("*.wav"):
        m = _CLONE_RE.match(path.name)
        if m:
            found.append((int(m.group(1)), path))
    return sorted(found)


@state.requires_consent
def prepare(seed=None):
    """Shuffle the clips into data/quiz/1.wav, 2.wav, ... with the same trim, rate and loudness,
    so only the voice itself gives anything away. Returns [{nr, path, label, real}]."""
    real = state.verified_recording("target")
    clones = _clones()
    if not clones:
        raise LabError("Nog geen klonen van de testzin gevonden. Voer eerst het experiment (stap 4) uit.")
    items = [("echt", real)] + [(f"kloon uit {s} s", p) for s, p in clones]
    random.Random(seed).shuffle(items)
    quiz_dir = state.subdir("quiz")
    for old in quiz_dir.glob("*.wav"):
        old.unlink()
    return [{"nr": nr, "path": audio.prepare_for_test(src, quiz_dir / f"{nr}.wav"), "label": label, "real": label == "echt"}
            for nr, (label, src) in enumerate(items, 1)]
