"""The listening-test zip: one real and three cloned clips of the target sentence."""

import zipfile

from . import audio, clone, state, texts
from .state import LabError

ZIP_NAMES = ["real.wav"] + [f"clone_{s}s.wav" for s in texts.REF_LENGTHS]


@state.requires_consent
def make_zip():
    info = state.consent()
    sources = [state.verified_recording("target")]
    for seconds in texts.REF_LENGTHS:
        path = clone.clone_path(texts.TARGET_ID, seconds)
        if not path.exists():
            raise LabError("Nog geen klonen gevonden. Voer eerst het experiment (stap 4) uit.")
        sources.append(path)
    test_dir = state.subdir("test")
    zip_path = state.data_dir() / f"{info['pair_code']}-{info['speaker']}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, src in zip(ZIP_NAMES, sources):
            dst = audio.prepare_for_test(src, test_dir / name)
            zf.write(dst, arcname=name)
    return zip_path


@state.requires_consent
def make_all_clips_zip():
    """Every clip, for the teacher's own demo set (the teacher consents to sharing their voice)."""
    zip_path = state.data_dir() / "alle_clips.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder in ("real", "clones"):
            for path in sorted(state.subdir(folder).glob("*.wav")):
                zf.write(path, arcname=f"{folder}/{path.name}")
    return zip_path
