import pytest

from lab import state
from lab.state import LabError


def test_consent_requires_valid_code_speaker_and_all_boxes():
    with pytest.raises(LabError):
        state.record_consent("K7Q", "A", [True] * 4)
    with pytest.raises(LabError):
        state.record_consent("K0QM", "A", [True] * 4)  # 0 is not in the alphabet
    with pytest.raises(LabError):
        state.record_consent("K7QM", "C", [True] * 4)
    with pytest.raises(LabError):
        state.record_consent("K7QM", "A", [True, True, False, True])
    info = state.record_consent(" k7qm ", "B", [True] * 4)
    assert info["pair_code"] == "K7QM" and info["speaker"] == "B"


def test_consent_stores_no_more_than_time_code_speaker():
    state.record_consent("K7QM", "A", [True] * 4)
    assert set(state.consent()) == {"time", "pair_code", "speaker"}


def test_guard_blocks_until_consent():
    @state.requires_consent
    def protected():
        return "ran"

    with pytest.raises(LabError):
        protected()
    state.record_consent("K7QM", "A", [True] * 4)
    assert protected() == "ran"


def test_replaced_recording_is_rejected(recordings):
    ref, _ = recordings
    assert state.verified_recording("reference") == ref
    ref.write_bytes(ref.read_bytes() + b"\0")
    with pytest.raises(LabError):
        state.verified_recording("reference")
