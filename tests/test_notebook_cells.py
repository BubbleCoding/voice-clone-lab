"""Run the notebook's visible code cells (steps 4, 5, 7) against a fake model."""

import pandas as pd
import pytest

from conftest import run_cell, run_experiment
from lab import clone, detect, state, texts
from lab.state import LabError

FREE_TEXT = '"Het regent vandaag in Amsterdam, dus ik neem de tram."'


def test_experiment_cell(recordings, fake_model):
    results = run_experiment()
    assert len(results) == len(texts.SENTENCES) * len(texts.REF_LENGTHS)
    for s in texts.SENTENCES:
        for n in texts.REF_LENGTHS:
            assert clone.clone_path(s["id"], n).exists()
    assert len(fake_model.conditioned) == len(texts.REF_LENGTHS)  # once per length, not per sentence
    assert fake_model.settings == {"exaggeration": 0.5, "cfg_weight": 0.5, "temperature": 0.8}


def test_experiment_cell_needs_consent(fake_model):
    with pytest.raises(LabError):
        run_experiment()


def test_free_mode_cell(recordings, fake_model):
    ns = run_cell("TEXT = ", replace={"CFG_WEIGHT = 0.5": "CFG_WEIGHT = 0.3"})
    assert ns["path"].exists() and ns["path"].name.startswith("vrij_")
    assert fake_model.settings["cfg_weight"] == 0.3


def test_free_mode_cell_refuses_scam_text(recordings, fake_model):
    with pytest.raises(LabError):
        run_cell("TEXT = ", replace={FREE_TEXT: '"Mam, maak snel geld over naar deze rekening"'})


def test_detection_cell(recordings, fake_model, monkeypatch):
    monkeypatch.setattr(detect, "fake_score", lambda wav, sr: 0.7)
    monkeypatch.setattr(detect, "watermark_score", lambda wav, sr: 1.0)
    run_experiment()
    ns = run_cell("for kind, path in detect.clips()")
    df = ns["df"]
    n_clips = 2 + len(texts.SENTENCES) * len(texts.REF_LENGTHS)  # leestekst + NL1_echt + clones
    assert len(df) == n_clips * len(detect.VERSIONS)
    assert set(df["versie"]) == set(detect.VERSIONS)
    assert (state.data_dir() / "detectie.csv").exists()
    summary = detect.summary(df)
    assert summary.loc[summary["soort"] == "kloon", "classifier_goed"].eq(1.0).all()
    assert summary.loc[summary["soort"] == "echt", "classifier_goed"].eq(0.0).all()
