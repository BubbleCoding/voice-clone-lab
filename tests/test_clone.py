import shutil

import pytest

from lab import clone, state, texts
from lab.state import LabError


def test_experiment_makes_every_sentence_at_every_length(recordings, fake_model):
    results = clone.run_experiment(progress=lambda _: None)
    assert len(results) == len(texts.SENTENCES) * len(texts.REF_LENGTHS)
    for s in texts.SENTENCES:
        for n in texts.REF_LENGTHS:
            assert clone.clone_path(s["id"], n).exists()
    # Conditioned once per reference length, not once per sentence.
    assert len(fake_model.conditioned) == len(texts.REF_LENGTHS)
    assert all(r["gen_s"] >= 0 and r["audio_s"] > 0 for r in results)


def test_reference_lengths_are_exact(recordings):
    from lab import audio
    paths = clone.make_references()
    for n, path in paths.items():
        assert audio.duration(audio.load(path)) == pytest.approx(n, abs=0.01)


def test_experiment_needs_consent(fake_model):
    with pytest.raises(LabError):
        clone.run_experiment()


def test_uploaded_reference_is_refused(recordings, fake_model, tmp_path):
    clone.make_references()
    # Replace the 10 s reference with someone else's audio: cloning must refuse it.
    other = tmp_path / "celebrity.wav"
    shutil.copy(state.subdir("real") / "NL1_echt.wav", other)
    from lab import audio
    audio.save(clone.reference_path(10), audio.load(other)[: 10 * audio.SR] * 0.5)
    with pytest.raises(LabError):
        clone.generate_free("Hallo, dit is een test.", "nl", 10)


@pytest.mark.parametrize("text", ["Mam, kun je snel geld overmaken?", "Send me the gift card code", "x" * 201, "  "])
def test_free_mode_refuses(text, recordings, fake_model):
    with pytest.raises(LabError):
        clone.generate_free(text, "nl", 10)


def test_free_mode_generates(recordings, fake_model):
    result = clone.generate_free("Het regent vandaag in Amsterdam.", "nl", 6)
    assert result["path"].exists() and result["path"].name.startswith("vrij_")
