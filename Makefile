# Teacher laptop commands. Students only use the Colab notebook.
PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python

.PHONY: test notebook

$(PY):
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip

test: $(PY)  ## unit tests (CPU only, no model downloads)
	$(PY) -m pip install -q -r requirements-dev.txt
	$(PY) -m pytest -q

notebook:  ## regenerate voice_clone_lab.ipynb from scripts/build_notebook.py
	$(PYTHON) scripts/build_notebook.py
