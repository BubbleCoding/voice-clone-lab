# Teacher laptop commands. Students only use the Colab notebook.
PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python
PAIRS ?= 20

.PHONY: setup-test serve-test pair-codes load-test wipe-test test notebook

$(PY):
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r listening_test/requirements.txt

setup-test: $(PY)  ## install the listening-test app in .venv

serve-test: $(PY)  ## serve the listening test on the classroom LAN (port 8000)
	$(PY) -m listening_test.serve

pair-codes: $(PY)  ## create PAIRS pair codes and open the printable cards
	$(PY) -m listening_test.pair_codes --n $(PAIRS)

load-test: $(PY)  ## 30 simulated raters for 2 minutes against a temporary server
	$(PY) -m listening_test.load_test --raters 30 --seconds 120

wipe-test: $(PY)  ## delete all uploaded clips, ratings and pair codes
	$(PY) -m listening_test.wipe

test: $(PY)  ## unit tests (CPU only, no model downloads)
	$(PY) -m pip install -q -r requirements-dev.txt
	$(PY) -m pytest -q

notebook:  ## regenerate voice_clone_lab.ipynb from scripts/build_notebook.py
	$(PYTHON) scripts/build_notebook.py
