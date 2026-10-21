import pytest

from lab import state
from lab.state import LabError


def test_consent_requires_all_boxes():
    with pytest.raises(LabError):
        state.record_consent([True, True, False, True])
    with pytest.raises(LabError):
        state.record_consent([])
    assert state.consent() is None
    state.record_consent([True] * 4)
    assert state.consent()


def test_consent_stores_only_the_time():
    state.record_consent([True] * 4)
    assert set(state.consent()) == {"time"}


def test_guard_blocks_until_consent():
    @state.requires_consent
    def protected():
        return "ran"

    with pytest.raises(LabError):
        protected()
    state.record_consent([True] * 4)
    assert protected() == "ran"


def test_replaced_recording_is_rejected(recordings):
    ref, _ = recordings
    assert state.verified_recording("reference") == ref
    ref.write_bytes(ref.read_bytes() + b"\0")
    with pytest.raises(LabError):
        state.verified_recording("reference")
