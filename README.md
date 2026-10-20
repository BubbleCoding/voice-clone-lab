# Jouw stem, hun scam: voice-clone lab

Workshop kit for HBO-ICT (HvA): students clone their own voice, run a blind listening test, and try to detect the fakes.

## Studenten

1. Open het notebook in Colab:
   **[voice_clone_lab.ipynb openen in Colab](https://colab.research.google.com/github/BubbleCoding/voice-clone-lab/blob/main/voice_clone_lab.ipynb)**
2. Start meteen cel 1 (setup, ongeveer 4 minuten) en volg daarna de stappen van boven naar beneden.
3. Sla **geen** kopie op in Drive. Aan het einde wis je alles met stap 8.

## Teacher

| Command | What it does |
| --- | --- |
| `make setup-test` | Install the listening-test app in `.venv` (needs Python 3.10+) |
| `make pair-codes` | Create 20 pair codes and open printable pair cards |
| `make serve-test` | Serve the listening test on the classroom LAN (port 8000); prints the URL and a QR code |
| `make load-test` | 30 simulated raters for 2 minutes against a temporary server |
| `make wipe-test` | Delete all uploaded clips, ratings and pair codes |
| `make test` | Unit tests (CPU only, no model downloads) |

Run the session from [`teacher/notes.md`](teacher/notes.md). The student handout is [`handout/handout.md`](handout/handout.md).

## Layout

`lab/` is the Python package the notebook imports (record, clone, detect, wipe); `lab/cells.py` holds the Dutch UI for each notebook cell. `listening_test/` is the Flask + SQLite app for the teacher laptop. `scripts/build_notebook.py` generates the notebook, so edit the cells there and run `make notebook`.

Models: [Chatterbox Multilingual V2 (V3 selectable)](https://github.com/resemble-ai/chatterbox) (MIT, Perth watermark) and [mo-thecreator/Deepfake-audio-detection](https://huggingface.co/mo-thecreator/Deepfake-audio-detection) (Apache-2.0).
