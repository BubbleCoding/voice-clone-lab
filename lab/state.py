"""Session state in data/state.json: consent and live recordings, plus the guards that enforce them."""

import functools
import hashlib
import json
import os
import re
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Same alphabet as listening_test/pair_codes.py: no 0/O, 1/I/L.
PAIR_CODE_RE = re.compile(r"^[ABCDEFGHJKMNPQRSTUVWXYZ23456789]{4}$")
SPEAKERS = ("A", "B")


class LabError(Exception):
    """An error with a Dutch message meant for students."""


def data_root():
    return Path(os.environ.get("VCL_DATA_DIR", REPO_ROOT / "data"))


def data_dir():
    path = data_root()
    path.mkdir(parents=True, exist_ok=True)
    return path


def subdir(name):
    path = data_dir() / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _state_path():
    return data_dir() / "state.json"


def load():
    path = _state_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(state):
    _state_path().write_text(json.dumps(state, indent=2))


def normalize_pair_code(code):
    return (code or "").strip().upper()


def record_consent(pair_code, speaker, statements_accepted):
    pair_code = normalize_pair_code(pair_code)
    if not PAIR_CODE_RE.match(pair_code):
        raise LabError("Ongeldige paircode. Gebruik de 4 tekens van jullie paarkaart.")
    if speaker not in SPEAKERS:
        raise LabError("Kies spreker A of B.")
    if not all(statements_accepted):
        raise LabError("Vink alle vier de verklaringen aan om verder te gaan.")
    state = load()
    # Only the timestamp, pair code and speaker letter. No names.
    state["consent"] = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "pair_code": pair_code, "speaker": speaker}
    _save(state)
    return state["consent"]


def consent():
    return load().get("consent")


def requires_consent(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not consent():
            raise LabError("Voer eerst de toestemmingscel (stap 2) uit en vink alle verklaringen aan.")
        return func(*args, **kwargs)
    return wrapper


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def register_recording(kind, path):
    """Remember a live recording so clone.py can refuse any other reference audio."""
    state = load()
    state.setdefault("recordings", {})[kind] = {"path": str(path), "sha256": sha256(path)}
    _save(state)


def verified_recording(kind):
    """Path of a live recording of this kind, or a LabError if it is missing or was replaced."""
    entry = load().get("recordings", {}).get(kind)
    if not entry or not Path(entry["path"]).exists():
        raise LabError(f"Geen opname gevonden. Voer eerst de opnamecel uit ({_KIND_HINT.get(kind, kind)}).")
    if sha256(entry["path"]) != entry["sha256"]:
        raise LabError("Deze opname is niet live in de opnamecel gemaakt. Neem opnieuw op in stap 3.")
    return Path(entry["path"])


def is_verified(path):
    """True if path is a reference cut from (or identical to) a live recording."""
    digest = sha256(path)
    state = load()
    known = [r["sha256"] for r in state.get("recordings", {}).values()]
    known += state.get("derived", [])
    return digest in known


def register_derived(path):
    """Register a file derived from a live recording, such as a 3 s reference cut."""
    state = load()
    derived = state.setdefault("derived", [])
    digest = sha256(path)
    if digest not in derived:
        derived.append(digest)
    _save(state)


_KIND_HINT = {"reference": "stap 3a, de leestekst", "target": "stap 3b, de testzin"}
