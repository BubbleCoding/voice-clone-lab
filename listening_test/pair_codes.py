"""Create pair codes and a printable page of pair cards: python -m listening_test.pair_codes --n 20"""

import argparse
import html
import re
import secrets
import webbrowser

from . import app as app_module

# Same alphabet as lab/state.py: no 0/O, 1/I/L.
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_RE = re.compile(rf"^[{ALPHABET}]{{4}}$")


def is_valid_format(code):
    return bool(CODE_RE.match(code or ""))


def new_code():
    return "".join(secrets.choice(ALPHABET) for _ in range(4))


def ensure_codes(base_dir, n):
    """Make sure at least n pair codes exist; returns all codes."""
    app_module.init_db(base_dir)
    conn = app_module.connect(base_dir / "listening.db")
    codes = [r[0] for r in conn.execute("SELECT code FROM pairs ORDER BY rowid")]
    while len(codes) < n:
        code = new_code()
        if code not in codes:
            conn.execute("INSERT INTO pairs (code) VALUES (?)", (code,))
            codes.append(code)
    conn.commit()
    conn.close()
    return codes


def cards_html(codes, url=""):
    cards = "".join(
        f"<div class='card'><div class='small'>Paarkaart · Jouw stem, hun scam</div>"
        f"<div class='code'>{html.escape(c)}</div>"
        f"<div class='small'>Spreker A en spreker B gebruiken dezelfde code.<br>"
        f"Notebook stap 2 en de luistertest{(' · ' + html.escape(url)) if url else ''}</div></div>"
        for c in codes)
    return ("<!doctype html><meta charset='utf-8'><title>Paarkaarten</title><style>"
            "body{font-family:sans-serif;margin:10mm}"
            ".grid{display:grid;grid-template-columns:repeat(2,1fr);gap:6mm}"
            ".card{border:1px dashed #555;padding:6mm;text-align:center;break-inside:avoid}"
            ".code{font:bold 48px monospace;letter-spacing:8px;margin:4mm 0}"
            ".small{font-size:12px;color:#333}</style>"
            f"<div class='grid'>{cards}</div>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--url", default="", help="listening-test URL to print on the cards")
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    base_dir = app_module.default_base_dir()
    codes = ensure_codes(base_dir, args.n)
    out = base_dir / "pair_cards.html"
    out.write_text(cards_html(codes, args.url))
    print(f"{len(codes)} pair codes: {' '.join(codes)}")
    print(f"Cards: {out}")
    if not args.no_open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
