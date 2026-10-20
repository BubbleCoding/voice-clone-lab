"""Generate voice_clone_lab.ipynb. Edit the cells here, then run: python scripts/build_notebook.py"""

import json
from pathlib import Path

REPO_URL = "https://github.com/BubbleCoding/voice-clone-lab"
OUT = Path(__file__).resolve().parent.parent / "voice_clone_lab.ipynb"

INTRO = f"""# Jouw stem, hun scam: voice-cloning lab

In dit notebook kloon je **je eigen stem** met een open-source AI-model (Chatterbox van Resemble AI). Daarna test je of mensen en detectoren het verschil horen.

**Spelregels**
- Je gebruikt alleen je eigen stem.
- Je deelt geen klonen buiten deze les.
- Aan het einde van de les wissen we alles samen (stap 8).

**Privacy:** je opnames worden tijdens de les verwerkt op servers van Google (Colab). Er wordt niets in Google Drive opgeslagen. **Sla geen kopie van dit notebook op in Drive** (Bestand → Kopie opslaan in Drive), dan blijft er niets van je stem achter.

Voer de cellen van boven naar beneden uit met ▶ of Shift+Enter. Code en uitleg: [{REPO_URL}]({REPO_URL})
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
import lab.cells as lab
lab.setup(player_mode=PLAYER, model=MODEL)'''

CELLS = [
    ("md", INTRO),
    ("md", "## 1. Setup\nStart deze cel meteen. Hij installeert alles en laadt de modellen. Wacht tot onderaan **✅ Alles werkt** staat.\n\n"
           "Zie je **❌ Geen GPU**? Kies *Runtime → Runtimetype wijzigen → T4 GPU* en voer de cel opnieuw uit."),
    ("code", SETUP),
    ("md", "## 2. Toestemming\nVul de code van jullie paarkaart in, kies of je spreker A of B bent, en vink de vier verklaringen aan. "
           "Zonder toestemming werken de volgende stappen niet."),
    ("code", "#@title 2. Toestemming\nlab.consent()"),
    ("md", "## 3a. Opnemen: leestekst\nDe browser vraagt om toegang tot je microfoon. Lees de tekst voor die verschijnt (ongeveer 20 seconden). "
           "Dit is het voorbeeld waarmee het model je stem kloont."),
    ("code", "#@title 3a. Leestekst opnemen\nlab.record_reference()"),
    ("md", "## 3b. Opnemen: testzin\nLees één zin voor. Deze echte opname komt straks in de luistertest, naast klonen van precies dezelfde zin."),
    ("code", "#@title 3b. Testzin opnemen\nlab.record_target()"),
    ("md", "## 4. Experiment: hoeveel stem is genoeg?\nHet model maakt vier zinnen (twee Nederlands, twee Engels) met **3, 6 en 10 seconden** van jouw stem als voorbeeld. "
           "Let op de generatietijd per clip.\n\nWist je dat Chatterbox nooit meer dan 10 seconden van je stem gebruikt? Meer audio maakt de kloon niet beter."),
    ("code", "#@title 4. Experiment\nlab.experiment()"),
    ("md", "## 5. Vrije modus\nTyp zelf een zin en hoor hem in jouw stem. Iemand anders nadoen of om geld, codes of gegevens vragen is **niet** toegestaan."),
    ("code", "#@title 5. Vrije modus\nlab.free_mode()"),
    ("md", "## 6. Downloaden voor de luistertest\nDit downloadt een zip met je echte testzin en drie klonen ervan. "
           "Upload die zip straks in de luistertest van de docent (het adres staat op het scherm)."),
    ("code", "#@title 6. Downloaden\nlab.download()"),
    ("md", "## 7. Detectie\nElke clip gaat langs een deepfake-classifier en een watermerk-detector (Chatterbox stopt een onhoorbaar watermerk in elke kloon). "
           "Daarna gebeurt hetzelfde na **MP3-compressie** en na een **telefoonlijn-filter**.\n\nWelke methode overleeft de telefoonlijn?"),
    ("code", "#@title 7. Detectie\nlab.detection()"),
    ("md", "## 8. Wissen\nAan het einde van de les, samen met de docent. Dit verwijdert al je opnames en klonen, en daarna de hele runtime.\n\n"
           "Kies daarna **Bewerken → Alle uitvoer wissen** en sluit het tabblad zonder op te slaan."),
    ("code", "#@title 8. Alles wissen\nlab.wipe()"),
]


def cell(kind, source):
    lines = source.splitlines(keepends=True)
    if kind == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": lines}
    return {"cell_type": "code", "execution_count": None, "metadata": {"cellView": "form"},
            "outputs": [], "source": lines}


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
