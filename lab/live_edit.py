"""Apply edits to lab/*.py before the next notebook cell runs.

IPython's %autoreload cannot be used: Colab's IPython imports the `imp` module, which
Python 3.12 removed. Instead, before each cell we reload every lab module (in import
order) once any lab file has changed. Modules keep their loaded models and servers
because they read them back with globals().get.
"""

import importlib
import sys
from pathlib import Path

# Dependencies first, so each module picks up the fresh version of what it imports.
ORDER = ["state", "texts", "audio", "colab_io", "player", "clone", "detect", "quiz", "package", "wipe", "checks", "cells"]

LAB_DIR = Path(__file__).resolve().parent
_mtimes = globals().get("_mtimes")
_installed = globals().get("_installed", False)


def _snapshot():
    return {p.name: p.stat().st_mtime_ns for p in LAB_DIR.glob("*.py")}


def reload_if_changed():
    """Reload all lab modules if any lab file changed since the last check. Returns True if it reloaded."""
    global _mtimes
    now = _snapshot()
    if _mtimes is None or now == _mtimes:
        _mtimes = now
        return False
    _mtimes = now
    for name in ORDER:
        module = sys.modules.get(f"lab.{name}")
        if module is not None:
            importlib.reload(module)
    return True


def _before_cell(*args):
    try:
        reload_if_changed()
    except Exception as e:  # a syntax error in an edited file: report it, keep the old code running
        print(f"⚠️ Je wijziging in lab/ kon niet geladen worden: {type(e).__name__}: {e}")


def install():
    global _installed
    try:
        from IPython import get_ipython
    except ImportError:
        return
    ip = get_ipython()
    if ip is None or _installed:
        return
    reload_if_changed()  # take the first snapshot
    ip.events.register("pre_run_cell", _before_cell)
    _installed = True
