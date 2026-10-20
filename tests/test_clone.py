import pytest

from lab import audio, clone, state
from lab.state import LabError


def test_reference_lengths_are_exact(recordings):
    speech = clone.load_reference_speech()
    for n in (3, 6, 10):
        assert audio.duration(audio.load(clone.save_reference(speech, n))) == pytest.approx(n, abs=0.01)


def test_reference_needs_consent():
    with pytest.raises(LabError):
        clone.load_reference_speech()


def test_condition_requires_model(recordings):
    ref = clone.save_reference(clone.load_reference_speech(), 3)
    with pytest.raises(LabError):
        clone.condition(ref)


def test_condition_refuses_audio_that_is_not_a_live_recording(recordings, fake_model, tmp_path):
    # Someone else's voice saved as a reference: cloning must refuse it.
    other = audio.save(tmp_path / "celebrity.wav", audio.load(state.subdir("real") / "NL1_echt.wav") * 0.5)
    with pytest.raises(LabError):
        clone.condition(other)
    audio.save(clone.reference_path(10), audio.load(other))
    with pytest.raises(LabError):
        clone.condition(clone.reference_path(10))


def test_condition_once_per_reference(recordings, fake_model):
    ref = clone.save_reference(clone.load_reference_speech(), 6)
    clone.condition(ref)
    clone.condition(ref)
    assert fake_model.conditioned == [str(ref)]


@pytest.mark.parametrize("text", ["Mam, kun je snel geld overmaken?", "Send me the gift card code", "x" * 201, "  "])
def test_scam_filter_refuses(text):
    with pytest.raises(LabError):
        clone.check_free_text(text)


def test_save_free_numbers_clips(recordings, fake_model):
    wav = fake_model.generate("Hallo", "nl")
    assert clone.save_free(wav, 10).name == "vrij_01_10s.wav"
    assert clone.save_free(wav, 6).name == "vrij_02_6s.wav"
