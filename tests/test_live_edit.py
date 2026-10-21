import os

from lab import clone, live_edit, texts


def test_edit_to_lab_file_is_picked_up_and_model_survives(monkeypatch):
    clone.MODEL = sentinel = object()
    live_edit._mtimes = None
    assert live_edit.reload_if_changed() is False  # first snapshot

    path = live_edit.LAB_DIR / "texts.py"
    original = path.read_text()
    stat = path.stat()
    try:
        path.write_text(original.replace("FREE_MODE_MAX_CHARS = 200", "FREE_MODE_MAX_CHARS = 123"))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))
        assert live_edit.reload_if_changed() is True
        assert texts.FREE_MODE_MAX_CHARS == 123
        assert clone.MODEL is sentinel  # loaded model kept across the reload
    finally:
        path.write_text(original)
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        live_edit.reload_if_changed()
        clone.MODEL = None
    assert texts.FREE_MODE_MAX_CHARS == 200


def test_notebook_does_not_use_ipython_autoreload():
    from conftest import notebook_cell
    assert "autoreload" not in notebook_cell("ui.setup(")


def test_reload_keeps_lab_error_class():
    from lab import state
    before = state.LabError
    live_edit._mtimes = {}
    live_edit.reload_if_changed()
    assert state.LabError is before and clone.LabError is before
