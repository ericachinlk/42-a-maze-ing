VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
MAIN = a_maze_ing.py

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy

run:
	$(PYTHON) $(MAIN) config.txt

debug:
	DEBUG=1 $(PYTHON) $(MAIN) config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 . --exclude=venv,__pycache__,.mypy_cache
	mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs --exclude venv

lint-strict:
	flake8 . --exclude=venv,__pycache__,.mypy_cache
	mypy . --strict --exclude venv

uninstall: clean
	rm -rf venv
