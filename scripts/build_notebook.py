"""Generate voice_clone_lab.ipynb. Edit the cells here, then run: python scripts/build_notebook.py"""

import json
from pathlib import Path

REPO_URL = "https://github.com/BubbleCoding/voice-clone-lab"
LAB_URL = f"{REPO_URL}/blob/main/lab"
OUT = Path(__file__).resolve().parent.parent / "voice_clone_lab.ipynb"

INTRO = f"""# Jouw stem, hun scam: voice-cloning lab

In dit notebook kloon je **je eigen stem** met een open-source AI-model (Chatterbox van Resemble AI). Daarna test je of mensen en detectoren het verschil horen.

**Spelregels**
- Je gebruikt alleen je eigen stem.
- Je deelt geen klonen buiten deze les.
- Aan het einde van de les wissen we alles samen (stap 8).

**Privacy:** je opnames worden tijdens de les verwerkt op servers van Google (Colab). Er wordt niets in Google Drive opgeslagen. **Sla geen kopie van dit notebook op in Drive** (Bestand → Kopie opslaan in Drive), dan blijft er niets van je stem achter.

Voer de cellen van boven naar beneden uit met ▶ of Shift+Enter.

### Onder de motorkap

De kern staat gewoon in dit notebook: het klonen (stap 4 en 5) en de detectie (stap 7) zijn leesbare Python. Pas ze gerust aan en voer de cel opnieuw uit.

Het loodgieterswerk zit in het pakket `lab/`. Open het via het 📁-icoon links: `voice-clone-lab/lab/`. Dubbelklik op een bestand om het te bewerken; je wijziging werkt bij de volgende cel die je uitvoert.

| Bestand | Wat erin zit |
| --- | --- |
| [`clone.py`]({LAB_URL}/clone.py) | Model laden, referenties knippen, de eigen-stem-controle, het scamfilter |
| [`audio.py`]({LAB_URL}/audio.py) | Knippen, pauzes inkorten, volume, en de MP3- en telefoonlijnfilters |
| [`detect.py`]({LAB_URL}/detect.py) | De deepfake-classifier en de watermerkdetector |
| [`colab_io.py`]({LAB_URL}/colab_io.py) | De microfoonopname in je browser (JavaScript) |
| [`texts.py`]({LAB_URL}/texts.py) | De vaste zinnen en de lijst met verboden woorden |
| [`state.py`]({LAB_URL}/state.py) | Toestemming en de controle dat een opname echt live was |
| [`cells.py`]({LAB_URL}/cells.py) | Knoppen, meldingen en tabellen |

**Eerlijk is eerlijk:** omdat je alle code kunt aanpassen, kun je ook de controles weghalen (alleen je eigen stem, het scamfilter). Doe dat niet. Dat het zo makkelijk kan, bespreken we aan het einde van de les.
"""

SETUP = f'''#@title 1. Setup: start deze cel meteen (duurt ongeveer 4 minuten)
PLAYER = "proxy"  #@param ["proxy", "embed"]
MODEL = "v2"  #@param ["v2", "v3"]
import os
REPO_URL = "{REPO_URL}"
REPO_DIR = "/content/voice-clone-lab"
if not os.path.isdir(REPO_DIR):
    !git clone -q --depth 1 {{REPO_URL}} {{REPO_DIR}}
%cd {{REPO_DIR}}
if not os.path.exists("/content/.vcl_installed"):
    !bash scripts/install_colab.sh && touch /content/.vcl_installed
# Edits to the files in lab/ take effect the next time you run a cell.
%load_ext autoreload
%autoreload 2
import time
import pandas as pd
from IPython.display import display
from lab import audio, clone, detect, player, state, texts
from lab import cells as ui
ui.setup(player_mode=PLAYER, model=MODEL)'''

EXPERIMENT = '''# Settings: change them and run the cell again.
REF_LENGTHS = [3, 6, 10]   # seconds of your voice; Chatterbox never uses more than 10
SETTINGS = dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.8)

model = clone.require_model()             # Chatterbox Multilingual, loaded in step 1
speech = clone.load_reference_speech()    # your recording from step 3a, long pauses shortened

results = []
for seconds in REF_LENGTHS:
    # 1. Cut the first N seconds of your voice. This is all the model gets to hear of you.
    ref = clone.save_reference(speech, seconds)

    # 2. The model "listens": it turns the clip into a speaker embedding and voice tokens.
    #    clone.condition() first checks that ref was cut from your own live recording,
    #    then calls model.prepare_conditionals(ref).
    clone.condition(ref)

    for sentence in texts.SENTENCES:
        # 3. Generate the sentence in your voice. Chatterbox adds an inaudible watermark.
        start = time.perf_counter()
        wav = model.generate(sentence["text"], language_id=sentence["lang"], **SETTINGS)
        took = time.perf_counter() - start

        path = clone.save_clone(wav, sentence["id"], seconds)
        results.append({"zin": sentence["id"], "referentie_s": seconds, "generatietijd_s": took, "path": path})
        print(f"{sentence['id']} uit {seconds} s stem: {took:.1f} s")

ui.show_experiment(results)'''

FREE_MODE = '''TEXT = "Het regent vandaag in Amsterdam, dus ik neem de tram."  #@param {type:"string"}
LANG = "nl"  #@param ["nl", "en"]
REFERENCE_S = 10  #@param [3, 6, 10] {type:"raw"}
EXAGGERATION = 0.5  #@param {type:"slider", min:0.25, max:1.5, step:0.05}
CFG_WEIGHT = 0.5  #@param {type:"slider", min:0, max:1, step:0.05}
TEMPERATURE = 0.8  #@param {type:"slider", min:0.4, max:1.2, step:0.05}
# Lower CFG: calmer pace, less accent from the reference. Higher exaggeration: more dramatic.
# Lower temperature: more stable, less variation.

text = clone.check_free_text(TEXT)   # the scam filter, see lab/texts.py

model = clone.require_model()
ref = clone.save_reference(clone.load_reference_speech(), REFERENCE_S)
clone.condition(ref)

start = time.perf_counter()
wav = model.generate(text, language_id=LANG, exaggeration=EXAGGERATION,
                     cfg_weight=CFG_WEIGHT, temperature=TEMPERATURE)
path = clone.save_free(wav, REFERENCE_S)
player.show(path, f"Gegenereerd in {time.perf_counter() - start:.1f} s")'''

DETECTION = '''rows = []
for kind, path in detect.clips():           # your real recordings ("echt") and every clone ("kloon")
    print("Bezig:", path.name)
    for version in detect.VERSIONS:         # origineel, mp3 (128 kbps), telefoon (8 kHz, 300-3400 Hz, mu-law, ruis)
        wav, sr = audio.load_native(detect.degraded(path, version))

        fake = detect.fake_score(wav, sr)       # deepfake classifier: probability (0-1) that this is fake
        mark = detect.watermark_score(wav, sr)  # Perth watermark: ~1.0 = made by Chatterbox, ~0.0 = not

        rows.append({
            "clip": path.stem,
            "soort": kind,
            "versie": version,
            "classifier_nep_score": round(fake, 2),
            "classifier_oordeel": "nep" if fake >= 0.5 else "echt",
            "classifier_goed": (fake >= 0.5) == (kind == "kloon"),
            "watermerk": round(mark, 2),
        })

df = pd.DataFrame(rows)
df.to_csv(state.data_dir() / "detectie.csv", index=False)
display(df)
print("Samenvatting (classifier_goed = aandeel juist beoordeeld):")
display(detect.summary(df))'''

CELLS = [
    ("md", INTRO),
    ("md", "## 1. Setup\nStart deze cel meteen. Hij installeert alles en laadt de modellen. Wacht tot onderaan **✅ Alles werkt** staat.\n\n"
           "Zie je **❌ Geen GPU**? Kies *Runtime → Runtimetype wijzigen → T4 GPU* en voer de cel opnieuw uit."),
    ("form", SETUP),
    ("md", "## 2. Toestemming\nVul de code van jullie paarkaart in, kies of je spreker A of B bent, en vink de vier verklaringen aan. "
           "Zonder toestemming werken de volgende stappen niet."),
    ("code", "ui.consent()"),
    ("md", "## 3a. Opnemen: leestekst\nDe browser vraagt om toegang tot je microfoon. Lees de tekst voor die verschijnt (ongeveer 20 seconden). "
           "Dit is het voorbeeld waarmee het model je stem kloont. Neem op in een stille hoek: het model kopieert ook ruis.\n\n"
           f"Hoe de opname werkt: [`colab_io.py`]({LAB_URL}/colab_io.py)."),
    ("code", "ui.record_reference()"),
    ("md", "## 3b. Opnemen: testzin\nLees één zin voor. Deze echte opname komt straks in de luistertest, naast klonen van precies dezelfde zin."),
    ("code", "ui.record_target()"),
    ("md", "## 4. Experiment: hoeveel stem is genoeg?\nDit is de hele kloon-code. Het model maakt vier zinnen (twee Nederlands, twee Engels) "
           "met **3, 6 en 10 seconden** van jouw stem als voorbeeld. Let op de generatietijd per clip.\n\n"
           "Wist je dat Chatterbox nooit meer dan 10 seconden van je stem gebruikt? Meer audio maakt de kloon niet beter.\n\n"
           "Laat `REF_LENGTHS` op 3, 6 en 10 staan voor de luistertest. Daarna mag je alles proberen."),
    ("code", EXPERIMENT),
    ("md", "## 5. Vrije modus\nTyp rechts een zin en speel met de instellingen. Iemand anders nadoen of om geld, codes of gegevens vragen is **niet** toegestaan."),
    ("code", FREE_MODE),
    ("md", "## 6. Downloaden voor de luistertest\nDit downloadt een zip met je echte testzin en drie klonen ervan (3, 6 en 10 s). "
           "Upload die zip straks in de luistertest van de docent (het adres staat op het scherm)."),
    ("code", "ui.download()"),
    ("md", "## 7. Detectie\nElke clip gaat langs een deepfake-classifier en een watermerk-detector (Chatterbox stopt een onhoorbaar watermerk in elke kloon). "
           "Daarna gebeurt hetzelfde na **MP3-compressie** en na een **telefoonlijn-filter**.\n\n"
           f"Welke methode overleeft de telefoonlijn? Wil je het filter aanpassen? Het staat in `phone_line()` in [`audio.py`]({LAB_URL}/audio.py)."),
    ("code", DETECTION),
    ("md", "## 8. Wissen\nAan het einde van de les, samen met de docent. Dit verwijdert al je opnames en klonen, en daarna de hele runtime.\n\n"
           "Kies daarna **Bewerken → Alle uitvoer wissen** en sluit het tabblad zonder op te slaan."),
    ("code", "ui.wipe()"),
]


def cell(kind, source):
    lines = source.splitlines(keepends=True)
    if kind == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": lines}
    metadata = {"cellView": "form"} if kind == "form" else {}
    return {"cell_type": "code", "execution_count": None, "metadata": metadata, "outputs": [], "source": lines}


def build():
    nb = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"gpuType": "T4", "provenance": [], "toc_visible": True},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "cells": [cell(k, s) for k, s in CELLS],
    }
    OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    return OUT


if __name__ == "__main__":
    print(f"Wrote {build()}")
