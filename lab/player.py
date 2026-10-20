"""Inline audio without embedding audio in the notebook.

Clips are served by a small file server on the runtime. Outputs contain only URLs,
which stop working when the runtime is deleted. MODE = "embed" is the fallback if the
proxy does not work in a browser; then outputs do contain audio and must be cleared.
"""

import functools
import html
import http.server
import socket
import threading
from pathlib import Path

from . import colab_io, state

MODE = "proxy"  # "proxy" or "embed"

_server = None
_base_url = None


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
    global _server, _base_url
    if _server is not None:
        return _base_url
    port = _free_port()
    handler = functools.partial(_QuietHandler, directory=str(state.data_dir()))
    # Colab's proxy reaches the kernel VM's ports; the VM itself is not publicly reachable.
    host = "0.0.0.0" if colab_io.in_colab() else "127.0.0.1"
    _server = http.server.ThreadingHTTPServer((host, port), handler)
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    _base_url = colab_io.proxy_url(port) if colab_io.in_colab() else f"http://127.0.0.1:{port}/"
    if not _base_url.endswith("/"):
        _base_url += "/"
    return _base_url


def stop():
    global _server, _base_url
    if _server is not None:
        _server.shutdown()
        _server.server_close()
    _server = None
    _base_url = None


def _audio_tag(path):
    path = Path(path)
    if MODE == "embed":
        from IPython.display import Audio
        return Audio(str(path))._repr_html_()
    base = start()
    rel = path.resolve().relative_to(state.data_dir().resolve()).as_posix()
    src = f"{base}{rel}?v={int(path.stat().st_mtime_ns)}"
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
