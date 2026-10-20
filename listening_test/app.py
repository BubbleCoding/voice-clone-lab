"""Blind listening test: pairs upload one real and three cloned clips, raters judge 'echt' or 'nep'."""

import io
import os
import secrets
import sqlite3
import time
import zipfile
from pathlib import Path

import numpy as np
import soundfile as sf
from flask import Flask, abort, g, jsonify, redirect, render_template, request, send_file, url_for

from .pair_codes import is_valid_format

ZIP_CATEGORIES = {"real.wav": "echt", "clone_3s.wav": "3s", "clone_6s.wav": "6s", "clone_10s.wav": "10s"}
CATEGORY_LABELS = {"echt": "Echt", "3s": "Kloon 3 s", "6s": "Kloon 6 s", "10s": "Kloon 10 s"}
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_CLIP_SECONDS = 30
SCHEMA = (Path(__file__).parent / "schema.sql").read_text()


def default_base_dir():
    return Path(os.environ.get("VCL_LT_DIR", Path(__file__).parent / "var"))


def connect(db_path):
    conn = sqlite3.connect(db_path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(base_dir):
    base_dir = Path(base_dir)
    (base_dir / "uploads").mkdir(parents=True, exist_ok=True)
    conn = connect(base_dir / "listening.db")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


class UploadError(Exception):
    pass


def read_upload(file_bytes):
    """Validate a notebook zip and decode its four clips. Returns {category: (wav, sr)}."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(file_bytes))
    except zipfile.BadZipFile:
        raise UploadError("Dit is geen geldig zip-bestand. Upload de zip uit stap 6 van het notebook.")
    members = {}
    for info in zf.infolist():
        name = Path(info.filename).name
        if info.is_dir() or name.startswith(".") or "__MACOSX" in info.filename:
            continue
        if name not in ZIP_CATEGORIES:
            raise UploadError(f"Onverwacht bestand in de zip: {name}")
        if info.file_size > MAX_MEMBER_BYTES:
            raise UploadError(f"{name} is te groot.")
        members[name] = info
    missing = set(ZIP_CATEGORIES) - set(members)
    if missing:
        raise UploadError("De zip mist: " + ", ".join(sorted(missing)))
    clips = {}
    for name, info in members.items():
        try:
            wav, sr = sf.read(io.BytesIO(zf.read(info)), dtype="float32", always_2d=False)
        except Exception:
            raise UploadError(f"{name} is geen leesbaar WAV-bestand.")
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        seconds = len(wav) / sr
        if not 0.5 <= seconds <= MAX_CLIP_SECONDS:
            raise UploadError(f"{name} is {seconds:.1f} s lang; verwacht tussen 0,5 en {MAX_CLIP_SECONDS} s.")
        clips[ZIP_CATEGORIES[name]] = (wav, sr)
    return clips


def results(db):
    rows = db.execute(
        "SELECT c.category, COUNT(r.id) AS n, COALESCE(SUM(r.correct), 0) AS correct "
        "FROM clips c LEFT JOIN ratings r ON r.clip_id = c.id GROUP BY c.category").fetchall()
    by_cat = {r["category"]: r for r in rows}
    categories = []
    for key, label in CATEGORY_LABELS.items():
        n = by_cat[key]["n"] if key in by_cat else 0
        correct = by_cat[key]["correct"] if key in by_cat else 0
        categories.append({"key": key, "label": label, "n": n, "correct": correct,
                           "pct": round(100 * correct / n) if n else None})
    clone_n = sum(c["n"] for c in categories if c["key"] != "echt")
    clone_fooled = sum(c["n"] - c["correct"] for c in categories if c["key"] != "echt")
    totals = db.execute(
        "SELECT (SELECT COUNT(*) FROM ratings) AS ratings,"
        " (SELECT COUNT(DISTINCT rater_id) FROM ratings) AS raters,"
        " (SELECT COUNT(DISTINCT pair_code || speaker) FROM clips) AS uploads").fetchone()
    return {"categories": categories, "ratings": totals["ratings"], "raters": totals["raters"],
            "uploads": totals["uploads"],
            "clones_marked_real_pct": round(100 * clone_fooled / clone_n) if clone_n else None,
            "time": time.time()}


def create_app(base_dir=None):
    base_dir = Path(base_dir or default_base_dir())
    init_db(base_dir)
    app = Flask(__name__)
    app.config.update(BASE_DIR=base_dir, DB_PATH=base_dir / "listening.db", UPLOAD_DIR=base_dir / "uploads",
                      MAX_CONTENT_LENGTH=40 * 1024 * 1024, SECRET_KEY=secrets.token_hex(16))

    def db():
        if "db" not in g:
            g.db = connect(app.config["DB_PATH"])
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    def pair_exists(code):
        return db().execute("SELECT 1 FROM pairs WHERE code = ?", (code,)).fetchone() is not None

    def rater():
        code = request.cookies.get("rater_code", "")
        rater_id = request.cookies.get("rater_id", "")
        if not (code and rater_id and pair_exists(code)):
            return None
        return code, rater_id

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if request.method == "GET":
            return render_template("upload.html")
        code = request.form.get("code", "").strip().upper()
        speaker = request.form.get("speaker", "")
        file = request.files.get("file")
        try:
            if not (is_valid_format(code) and pair_exists(code)):
                raise UploadError("Onbekende paircode. Gebruik de code van jullie paarkaart.")
            if speaker not in ("A", "B"):
                raise UploadError("Kies spreker A of B.")
            if file is None or not file.filename:
                raise UploadError("Kies eerst de zip uit het notebook.")
            clips = read_upload(file.read())
        except UploadError as e:
            return render_template("upload.html", error=str(e), code=code, speaker=speaker), 400

        conn = db()
        upload_dir = app.config["UPLOAD_DIR"]
        old = conn.execute("SELECT id FROM clips WHERE pair_code = ? AND speaker = ?", (code, speaker)).fetchall()
        for row in old:
            conn.execute("DELETE FROM ratings WHERE clip_id = ?", (row["id"],))
            conn.execute("DELETE FROM clips WHERE id = ?", (row["id"],))
            (upload_dir / f"{row['id']}.wav").unlink(missing_ok=True)
        for category, (wav, sr) in clips.items():
            clip_id = secrets.token_hex(8)
            # Re-encode: drops metadata and gives every clip the same container format.
            sf.write(str(upload_dir / f"{clip_id}.wav"), np.clip(wav, -1, 1), sr, subtype="PCM_16")
            conn.execute("INSERT INTO clips (id, pair_code, speaker, category, created) VALUES (?, ?, ?, ?, ?)",
                         (clip_id, code, speaker, category, time.time()))
        conn.commit()
        return render_template("upload.html", success=True, replaced=bool(old), code=code, speaker=speaker)

    @app.route("/beoordelen", methods=["GET", "POST"])
    def rate():
        if request.method == "POST":
            code = request.form.get("code", "").strip().upper()
            if not (is_valid_format(code) and pair_exists(code)):
                return render_template("rate_login.html", error="Onbekende paircode.", code=code), 400
            resp = redirect(url_for("rate"))
            resp.set_cookie("rater_code", code, max_age=6 * 3600, samesite="Lax")
            if not request.cookies.get("rater_id"):
                resp.set_cookie("rater_id", secrets.token_hex(8), max_age=6 * 3600, samesite="Lax")
            return resp
        who = rater()
        if who is None:
            return render_template("rate_login.html")
        return render_template("rate.html", code=who[0])

    @app.get("/uitloggen")
    def logout():
        resp = redirect(url_for("rate"))
        resp.delete_cookie("rater_code")
        return resp

    @app.get("/api/next")
    def api_next():
        who = rater()
        if who is None:
            return jsonify(error="login"), 401
        code, rater_id = who
        conn = db()
        # Never your own pair's clips, never a clip twice; least-rated clips first.
        row = conn.execute(
            "SELECT c.id FROM clips c "
            "WHERE c.pair_code != ? AND c.id NOT IN (SELECT clip_id FROM ratings WHERE rater_id = ?) "
            "ORDER BY (SELECT COUNT(*) FROM ratings r WHERE r.clip_id = c.id), RANDOM() LIMIT 1",
            (code, rater_id)).fetchone()
        rated = conn.execute("SELECT COUNT(*) FROM ratings WHERE rater_id = ?", (rater_id,)).fetchone()[0]
        available = conn.execute("SELECT COUNT(*) FROM clips WHERE pair_code != ?", (code,)).fetchone()[0]
        if row is None:
            return jsonify(done=True, rated=rated, available=available)
        return jsonify(done=False, clip_id=row["id"], url=url_for("clip", clip_id=row["id"]),
                       rated=rated, available=available)

    @app.post("/api/rate")
    def api_rate():
        who = rater()
        if who is None:
            return jsonify(error="login"), 401
        code, rater_id = who
        data = request.get_json(silent=True) or {}
        answer = data.get("answer")
        if answer not in ("echt", "nep"):
            return jsonify(error="answer"), 400
        conn = db()
        clip = conn.execute("SELECT category, pair_code FROM clips WHERE id = ?", (data.get("clip_id"),)).fetchone()
        if clip is None or clip["pair_code"] == code:
            return jsonify(error="clip"), 400
        correct = int((answer == "echt") == (clip["category"] == "echt"))
        conn.execute("INSERT OR IGNORE INTO ratings (clip_id, rater_code, rater_id, answer, correct, created) "
                     "VALUES (?, ?, ?, ?, ?, ?)", (data["clip_id"], code, rater_id, answer, correct, time.time()))
        conn.commit()
        return jsonify(ok=True)

    @app.get("/api/me")
    def api_me():
        who = rater()
        if who is None:
            return jsonify(error="login"), 401
        row = db().execute("SELECT COUNT(*) AS n, COALESCE(SUM(correct), 0) AS correct FROM ratings WHERE rater_id = ?",
                           (who[1],)).fetchone()
        return jsonify(n=row["n"], correct=row["correct"])

    @app.get("/clip/<clip_id>")
    def clip(clip_id):
        if not clip_id.isalnum():
            abort(404)
        if db().execute("SELECT 1 FROM clips WHERE id = ?", (clip_id,)).fetchone() is None:
            abort(404)
        return send_file(app.config["UPLOAD_DIR"] / f"{clip_id}.wav", mimetype="audio/wav", max_age=0)

    @app.get("/resultaten")
    def results_page():
        return render_template("results.html")

    @app.get("/api/results")
    def api_results():
        return jsonify(results(db()))

    return app
