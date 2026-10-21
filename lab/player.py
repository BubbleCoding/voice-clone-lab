"""Inline audio without embedding audio in the notebook.

In Colab, each player fetches its clip from the kernel when it is displayed
(colab_io.kernel_audio_tag), so outputs contain only a file name and stop
playing when the runtime is deleted. Outside Colab, a small local file server does the
same. MODE = "embed" is the fallback; then outputs do contain audio and must be cleared.
"""

import base64
import functools
import html
import http.server
import socket
import threading
from pathlib import Path

from . import colab_io, state

MODE = globals().get("MODE", "live")  # "live" or "embed"
CALLBACK = "vcl.audio"

# globals().get keeps the running server when live_edit reloads this file after an edit.
_server = globals().get("_server")
_base_url = globals().get("_base_url")

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start():
    """Local file server for players outside Colab."""
    global _server, _base_url
    if _server is not None:
        return _base_url
    port = _free_port()
    handler = functools.partial(_QuietHandler, directory=str(state.data_dir()))
    _server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    _base_url = f"http://127.0.0.1:{port}/"
    return _base_url


def stop():
    global _server, _base_url
    if _server is not None:
        _server.shutdown()
        _server.server_close()
    _server = None
    _base_url = None


def serve_clip(rel):
    """Called from the browser: one clip from the data folder as base64 WAV."""
    from IPython.display import JSON
    root = state.data_dir().resolve()
    path = (root / rel).resolve()
    if root not in path.parents or not path.is_file():
        return JSON({"error": "not found"})
    return JSON({"data": base64.b64encode(path.read_bytes()).decode("ascii")})


def _audio_tag(path):
    path = Path(path)
    if MODE == "embed":
        from IPython.display import Audio
        return Audio(str(path))._repr_html_()
    rel = path.resolve().relative_to(state.data_dir().resolve()).as_posix()
    if colab_io.in_colab():
        colab_io.register_callback(CALLBACK, serve_clip)
        return colab_io.kernel_audio_tag(CALLBACK, rel)
    src = f"{start()}{rel}?v={int(path.stat().st_mtime_ns)}"
    return f'<audio controls preload="none" src="{html.escape(src)}"></audio>'


def cell(path):
    return _audio_tag(path) if path else "&mdash;"


def show(path, caption=""):
    from IPython.display import HTML, display
    cap = f"<div>{html.escape(caption)}</div>" if caption else ""
    display(HTML(f"{cap}{_audio_tag(path)}"))


def show_grid(header, rows):
    """rows: list of (label, [path or None, ...]) matching header[1:]."""
    from IPython.display import HTML, display
    th = "".join(f"<th style='padding:4px 8px'>{html.escape(h)}</th>" for h in header)
    body = ""
    for label, paths in rows:
        tds = "".join(f"<td style='padding:4px 8px'>{cell(p)}</td>" for p in paths)
        body += f"<tr><td style='padding:4px 8px;max-width:260px'>{html.escape(label)}</td>{tds}</tr>"
    display(HTML(f"<table style='border-collapse:collapse'><tr>{th}</tr>{body}</table>"))
