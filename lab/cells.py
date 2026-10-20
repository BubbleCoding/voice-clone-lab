"""The functions the notebook cells call, with a Dutch UI. All logic lives in the other modules."""

import functools
import html
import time

from . import audio, checks, clone, colab_io, detect, package, player, state, texts, wipe as wipe_mod
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


def _require_colab(what):
    if not colab_io.in_colab():
        raise LabError(f"{what} werkt alleen in Google Colab.")


# 1. Setup

@friendly
def setup(player_mode="proxy", model="v3"):
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


# 4. Experiment

@friendly
def experiment():
    import pandas as pd
    from IPython.display import display
    t0 = time.perf_counter()
    results = clone.run_experiment()
    total = time.perf_counter() - t0
    real_target = state.subdir("real") / f"{texts.TARGET_ID}_echt.wav"
    header = ["Zin", "Echt"] + [f"Kloon {s} s" for s in texts.REF_LENGTHS]
    rows = []
    for s in texts.SENTENCES:
        real = real_target if s["id"] == texts.TARGET_ID and real_target.exists() else None
        rows.append((f"{s['id']}: {s['text']}", [real] + [clone.clone_path(s["id"], n) for n in texts.REF_LENGTHS]))
    player.show_grid(header, rows)
    table = pd.DataFrame([{k: v for k, v in r.items() if k != "path"} for r in results])
    table.columns = ["Zin", "Referentie (s)", "Audio (s)", "Generatietijd (s)", "Realtime-factor"]
    display(table)
    _ok(f"{len(results)} klonen gemaakt in {total:.0f} s. Zoveel moeite kost het dus.")


# 5. Free mode

@friendly
@state.requires_consent
def free_mode():
    import ipywidgets as w
    from IPython.display import display
    _show_html(f"<p style='color:#b00020'><b>{html.escape(texts.FREE_MODE_NOTICE)}</b></p>")
    text = w.Textarea(placeholder="Typ een zin...", layout=w.Layout(width="520px", height="70px"))
    lang = w.Dropdown(options=[("Nederlands", "nl"), ("Engels", "en")], description="Taal:")
    seconds = w.Dropdown(options=[(f"{s} s", s) for s in texts.REF_LENGTHS], value=max(texts.REF_LENGTHS),
                         description="Referentie:")
    d = clone.GENERATION_DEFAULTS
    style = {"description_width": "110px"}
    exaggeration = w.FloatSlider(value=d["exaggeration"], min=0.25, max=1.5, step=0.05, description="Expressie:", style=style)
    cfg_weight = w.FloatSlider(value=d["cfg_weight"], min=0.0, max=1.0, step=0.05, description="CFG / tempo:", style=style)
    temperature = w.FloatSlider(value=d["temperature"], min=0.4, max=1.2, step=0.05, description="Temperatuur:", style=style)
    advanced = w.Accordion(children=[w.VBox([
        w.HTML("<small>Lagere CFG = rustiger tempo en minder accent van de referentie. "
               "Hogere expressie = dramatischer. Lagere temperatuur = stabieler.</small>"),
        exaggeration, cfg_weight, temperature])])
    advanced.set_title(0, "Geavanceerd")
    button = w.Button(description="Genereer", button_style="primary")
    out = w.Output()

    def on_click(_):
        out.clear_output()
        with out:
            try:
                button.disabled = True
                result = clone.generate_free(text.value, lang.value, seconds.value, exaggeration=exaggeration.value,
                                             cfg_weight=cfg_weight.value, temperature=temperature.value)
                player.show(result["path"], f"{result['audio_s']} s audio in {result['gen_s']} s gegenereerd")
            except LabError as e:
                _error(str(e))
            finally:
                button.disabled = False

    button.on_click(on_click)
    display(w.VBox([text, w.HBox([lang, seconds]), advanced, button, out]))


# 6. Download

@friendly
def download(all_clips=False):
    zip_path = package.make_all_clips_zip() if all_clips else package.make_zip()
    _ok(f"{zip_path.name} gemaakt. Upload dit bestand straks in de luistertest.")
    if colab_io.in_colab():
        colab_io.download(zip_path)


# 7. Detection

@friendly
def detection():
    from IPython.display import display
    df, csv_path, elapsed = detect.run()
    if df.empty:
        raise LabError("Geen clips gevonden. Voer eerst stap 3 en 4 uit.")
    display(df)
    print("\nSamenvatting (classifier_goed = aandeel juist beoordeeld):")
    display(detect.summary(df))
    _ok(f"{df['clip'].nunique()} clips × 3 versies getest in {elapsed:.0f} s. Tabel opgeslagen als {csv_path.name}.")


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
