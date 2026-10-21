"""A zip of every clip, for the teacher's own demo voicemail (the teacher consents to using their voice)."""

import zipfile

from . import state


@state.requires_consent
def make_all_clips_zip():
    zip_path = state.data_dir() / "alle_clips.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder in ("real", "clones"):
            for path in sorted(state.subdir(folder).glob("*.wav")):
                zf.write(path, arcname=f"{folder}/{path.name}")
    return zip_path
