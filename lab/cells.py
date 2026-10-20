"""Dutch UI for the notebook's plumbing cells (setup, consent, recording, download, wipe) and result displays."""

import functools
import html
import time

from . import audio, checks, clone, colab_io, package, player, state, texts, wipe as wipe_mod
from .state import LabError


def _show_html(markup):
    from IPython.display import HTML, display
    display(HTML(markup))


def _error(message):
    _show_html(f"<div style='color:#b00020;font-size:16px'>⛔ {html.escape(message)}</div>")


def _ok(message):
    _show_html(f"<div style='color:#0a7d32;font-size:16px'>✅ {html.escape(message)}</div>")


def friendly(func):
    """Show LabErrors as a Dutch message instead of a traceback."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LabError as e:
            _error(str(e))
    return wrapper


def _install_error_handler():
    """In the visible code cells, show a LabError as one Dutch line instead of a traceback."""
    try:
        from IPython import get_ipython
    except ImportError:
        return
    ip = get_ipython()
    if ip is not None:
        ip.set_custom_exc((LabError,), lambda shell, etype, value, tb, tb_offset=None: _error(str(value)))


def _require_colab(what):
    if not colab_io.in_colab():
        raise LabError(f"{what} werkt alleen in Google Colab.")


# 1. Setup

@friendly
def setup(player_mode="proxy", model="v2"):
    _install_error_handler()
    player.MODE = player_mode
    clone.VERSION = model
    t0 = time.perf_counter()
    print("Modellen laden en controleren. Dit duurt een paar minuten...\n")
    results = checks.run()
    failed = [name for name, ok, _ in results if not ok and name != "classifier"]
    print(f"\nKlaar in {time.perf_counter() - t0:.0f} s.")
    if failed:
        _error("Niet alles werkt. Lees de regels met ❌ hierboven, of vraag de docent.")
    else:
        _ok("Alles werkt. Ga verder met stap 2.")


# 2. Consent

@friendly
def consent():
    import ipywidgets as w
    code = w.Text(description="Paircode:", placeholder="bijv. K7QM", layout=w.Layout(width="220px"))
    speaker = w.ToggleButtons(options=["A", "B"], description="Spreker:")
    boxes = [w.Checkbox(description=s, indent=False, layout=w.Layout(width="auto")) for s in texts.CONSENT_STATEMENTS]
    button = w.Button(description="Bevestig", button_style="primary")
    out = w.Output()

    def on_click(_):
        out.clear_output()
        with out:
            try:
                info = state.record_consent(code.value, speaker.value, [b.value for b in boxes])
                _ok(f"Toestemming vastgelegd voor paar {info['pair_code']}, spreker {info['speaker']}. Ga verder met stap 3.")
            except LabError as e:
                _error(str(e))

    button.on_click(on_click)
    from IPython.display import display
    _show_html("<p>Je opnames worden tijdens de les verwerkt op servers van Google (Colab). "
               "Er wordt niets in Google Drive opgeslagen. Sla geen kopie van dit notebook op in Drive.</p>")
    display(w.VBox([code, speaker, *boxes, button, out]))


# 3. Record

def _record_to(kind, max_s, label, dst, check):
    _require_colab("Opnemen")
    try:
        raw = colab_io.record(max_s, label)
    except RuntimeError as e:
        raise LabError(f"Opnemen mislukt ({e}). Geef de browser toegang tot je microfoon, of gebruik de laptop van je partner.")
    wav = audio.trim(audio.decode_bytes(raw))
    check(wav)
    path = audio.save(dst, audio.normalize_loudness(wav))
    state.register_recording(kind, path)
    return path


@friendly
@state.requires_consent
def record_reference():
    _show_html(f"<p>Lees deze tekst rustig en duidelijk voor (ongeveer 20 seconden):</p>"
               f"<blockquote style='font-size:20px;line-height:1.5'>{html.escape(texts.READING_PASSAGE)}</blockquote>")

    def check(wav):
        speech = audio.speech_seconds(wav)
        if speech < texts.MIN_REFERENCE_SPEECH_S:
            raise LabError(f"Te weinig spraak opgenomen ({speech:.0f} s, minimaal {texts.MIN_REFERENCE_SPEECH_S:.0f} s). "
                           "Voer deze cel opnieuw uit en lees de hele tekst voor.")

    path = _record_to("reference", texts.MAX_REFERENCE_RECORDING_S, "Leestekst.",
                      state.subdir("real") / "leestekst.wav", check)
    _ok("Leestekst opgenomen. Luister terug, en neem opnieuw op als het niet goed klinkt.")
    player.show(path)


@friendly
@state.requires_consent
def record_target():
    target = texts.sentence(texts.TARGET_ID)
    _show_html(f"<p>Lees deze zin één keer voor, in je normale tempo:</p>"
               f"<blockquote style='font-size:20px'>{html.escape(target['text'])}</blockquote>")

    def check(wav):
        if audio.duration(wav) < 2.0:
            raise LabError("De opname is te kort. Voer deze cel opnieuw uit.")

    path = _record_to("target", texts.MAX_TARGET_RECORDING_S, "Testzin.",
                      state.subdir("real") / f"{texts.TARGET_ID}_echt.wav", check)
    _ok("Testzin opgenomen.")
    player.show(path)


# 4. Experiment (the loop itself is visible code in the notebook)

def show_experiment(results):
    """Player grid (real vs clones per sentence) and a timing table for the step-4 results."""
    import pandas as pd
    from IPython.display import display
    lengths = sorted({r["referentie_s"] for r in results})
    real_target = state.subdir("real") / f"{texts.TARGET_ID}_echt.wav"
    header = ["Zin", "Echt"] + [f"Kloon {n} s" for n in lengths]
    rows = []
    for s in texts.SENTENCES:
        real = real_target if s["id"] == texts.TARGET_ID and real_target.exists() else None
        paths = [clone.clone_path(s["id"], n) for n in lengths]
        rows.append((f"{s['id']}: {s['text']}", [real] + [p if p.exists() else None for p in paths]))
    player.show_grid(header, rows)
    table = pd.DataFrame([{
        "Zin": r["zin"],
        "Referentie (s)": r["referentie_s"],
        "Audio (s)": round(audio.duration(audio.load(r["path"])), 1),
        "Generatietijd (s)": round(r["generatietijd_s"], 1),
    } for r in results])
    table["Realtime-factor"] = (table["Generatietijd (s)"] / table["Audio (s)"]).round(2)
    display(table)
    total = sum(r["generatietijd_s"] for r in results)
    _ok(f"{len(results)} klonen gemaakt in {total:.0f} s rekentijd.")


# 6. Download

@friendly
def download(all_clips=False):
    zip_path = package.make_all_clips_zip() if all_clips else package.make_zip()
    _ok(f"{zip_path.name} gemaakt. Upload dit bestand straks in de luistertest.")
    if colab_io.in_colab():
        colab_io.download(zip_path)


# 8. Wipe

@friendly
def wipe():
    import ipywidgets as w
    from IPython.display import clear_output, display
    sure = w.Checkbox(description="Ik weet dat dit al mijn opnames en klonen verwijdert.", indent=False,
                      layout=w.Layout(width="auto"))
    button = w.Button(description="Alles wissen", button_style="danger")
    out = w.Output()

    def on_click(_):
        out.clear_output()
        with out:
            if not sure.value:
                _error("Vink eerst het vakje aan.")
                return
        wipe_mod.wipe_data()
        clear_output()
        left = wipe_mod.remaining_audio()
        if left:
            _error(f"Er staan nog {len(left)} audiobestanden op de runtime. Roep de docent.")
            return
        _ok("Alle opnames en klonen zijn verwijderd van de runtime.")
        _show_html("<ol style='font-size:16px'>"
                   "<li>Kies nu <b>Bewerken → Alle uitvoer wissen</b> (Edit → Clear all outputs).</li>"
                   "<li>Sla het notebook <b>niet</b> op in Drive, en sluit het tabblad.</li>"
                   "</ol><p>De runtime wordt over een paar seconden verwijderd.</p>")
        if colab_io.in_colab():
            time.sleep(3)
            colab_io.delete_runtime()

    button.on_click(on_click)
    display(w.VBox([sure, button, out]))
