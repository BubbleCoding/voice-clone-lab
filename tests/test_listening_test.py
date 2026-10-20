import io
import zipfile

import numpy as np
import pytest
import soundfile as sf

from listening_test.app import create_app, read_upload, UploadError
from listening_test.load_test import synthetic_zip
from listening_test.pair_codes import ensure_codes, is_valid_format


@pytest.fixture
def lt(tmp_path):
    codes = ensure_codes(tmp_path, 3)
    app = create_app(tmp_path)
    app.testing = True
    return app, codes


def upload(client, code, speaker, data):
    return client.post("/upload", data={"code": code, "speaker": speaker,
                                        "file": (io.BytesIO(data), f"{code}-{speaker}.zip")},
                       content_type="multipart/form-data")


def login(client, code):
    return client.post("/beoordelen", data={"code": code})


def test_codes_are_unambiguous(tmp_path):
    codes = ensure_codes(tmp_path, 50)
    assert len(set(codes)) == 50 and all(is_valid_format(c) for c in codes)
    assert not any(ch in "".join(codes) for ch in "0O1IL")


def test_upload_rejects_bad_zips():
    with pytest.raises(UploadError):
        read_upload(b"not a zip")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("real.wav", b"RIFF")
    with pytest.raises(UploadError):
        read_upload(buf.getvalue())


def test_upload_rejects_unknown_code(lt):
    app, _ = lt
    r = upload(app.test_client(), "ZZZZ", "A", synthetic_zip(1))
    assert r.status_code == 400


def test_rater_never_gets_own_pair_or_repeats(lt):
    app, codes = lt
    c = app.test_client()
    for i, code in enumerate(codes):
        assert upload(c, code, "A", synthetic_zip(i)).status_code == 200
    rater = app.test_client()
    login(rater, codes[0])
    seen = set()
    while True:
        data = rater.get("/api/next").get_json()
        if data["done"]:
            break
        assert data["clip_id"] not in seen
        seen.add(data["clip_id"])
        assert rater.get(data["url"]).data[:4] == b"RIFF"
        assert rater.post("/api/rate", json={"clip_id": data["clip_id"], "answer": "nep"}).status_code == 200
    assert len(seen) == 8  # two other pairs × four clips

    with app.app_context():
        from listening_test.app import connect
        conn = connect(app.config["DB_PATH"])
        own = {r[0] for r in conn.execute("SELECT id FROM clips WHERE pair_code = ?", (codes[0],))}
    assert not own & seen


def test_results_per_category(lt):
    app, codes = lt
    c = app.test_client()
    upload(c, codes[1], "A", synthetic_zip(1))
    rater = app.test_client()
    login(rater, codes[0])
    for _ in range(4):
        data = rater.get("/api/next").get_json()
        rater.post("/api/rate", json={"clip_id": data["clip_id"], "answer": "nep"})
    res = c.get("/api/results").get_json()
    by_key = {cat["key"]: cat for cat in res["categories"]}
    assert res["ratings"] == 4 and res["uploads"] == 1
    assert by_key["echt"]["pct"] == 0           # the real clip was called fake
    assert by_key["10s"]["pct"] == 100          # every clone was called fake
    assert res["clones_marked_real_pct"] == 0


def test_reupload_replaces_set(lt):
    app, codes = lt
    c = app.test_client()
    upload(c, codes[1], "A", synthetic_zip(1))
    upload(c, codes[1], "A", synthetic_zip(2))
    assert c.get("/api/results").get_json()["uploads"] == 1
    files = list((app.config["UPLOAD_DIR"]).glob("*.wav"))
    assert len(files) == 4


def test_clip_urls_reveal_nothing(lt):
    app, codes = lt
    c = app.test_client()
    upload(c, codes[1], "A", synthetic_zip(1))
    login(c, codes[0])
    data = c.get("/api/next").get_json()
    for word in ("real", "clone", "echt", "3s", "10s", codes[1]):
        assert word not in data["url"]


def test_rating_requires_login(lt):
    app, _ = lt
    assert app.test_client().get("/api/next").status_code == 401


def test_pages_render(lt):
    app, codes = lt
    c = app.test_client()
    for path in ("/", "/upload", "/beoordelen", "/resultaten"):
        assert c.get(path).status_code == 200, path
    login(c, codes[0])
    assert b"Echt of nep?" in c.get("/beoordelen").data
