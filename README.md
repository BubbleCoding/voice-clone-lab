# Jouw stem, hun scam: voice-clone lab

Workshop kit for HBO-ICT (HvA): students clone their own voice, test whether their partner can tell real from fake, try to detect the fakes, and discuss the dark side of voice cloning.

## Studenten

1. Open het notebook in Colab:
   **[voice_clone_lab.ipynb openen in Colab](https://colab.research.google.com/github/BubbleCoding/voice-clone-lab/blob/main/voice_clone_lab.ipynb)**
2. Start meteen cel 1 (setup, ongeveer 4 minuten) en volg daarna de stappen van boven naar beneden.
3. Sla **geen** kopie op in Drive. Aan het einde wis je alles met stap 8.

## Teacher

Everything runs in Colab; the teacher needs no server. Run the session from [`teacher/notes.md`](teacher/notes.md) and make the opening voicemail with [`teacher/demo-script.md`](teacher/demo-script.md). The student handout, with the scammer worksheet on the back, is [`handout/handout.html`](handout/handout.html): open it in a browser and print A4 double-sided. The slide rundown for a Dark Tech deck is [`teacher/slides-outline.md`](teacher/slides-outline.md); paste it into Claude to generate the .pptx.

| Command | What it does |
| --- | --- |
| `make test` | Unit tests (CPU only, no model downloads) |
| `make notebook` | Regenerate the notebook from `scripts/build_notebook.py` |

## Layout

`lab/` is the Python package the notebook imports (record, clone, quiz, detect, wipe); `lab/cells.py` holds the Dutch UI for each notebook cell. `scripts/build_notebook.py` generates the notebook, so edit the cells there and run `make notebook`.

Models: [Chatterbox Multilingual V2 (V3 selectable)](https://github.com/resemble-ai/chatterbox) (MIT, Perth watermark) and [mo-thecreator/Deepfake-audio-detection](https://huggingface.co/mo-thecreator/Deepfake-audio-detection) (Apache-2.0).
