.PHONY: pubs serve

VENV := .venv-bib
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Regenerate _data/publications_generated.yml from bibliography/*.bib
pubs: $(VENV)/bin/python
	$(PY) scripts/bib_to_jekyll.py

$(VENV)/bin/python:
	python3 -m venv $(VENV)
	$(PIP) install -q -r scripts/requirements-bib.txt

serve:
	export LANG=C.UTF-8 LC_ALL=C.UTF-8 && bundle exec jekyll serve --livereload
