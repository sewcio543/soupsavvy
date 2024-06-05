.PHONY: build

build:
	python -m build
	twine check dist/*
setup:
	python -m pip install -r requirements.txt
	python -m pip install -r requirements_dev.txt
	python -m pip install -r docs/requirements.txt
install:
	python -m pip install -e .
	python -m pip show soupsavvy
lint:
	python -m flake8 --config tox.ini
format:
	black . --line-length 88 --diff --check
test:
	python -m pytest
coverage:
	python -m coverage run -m pytest
	python -m coverage report
	python -m coverage html
typecheck:
	python -m mypy . || true
	python -m mypy --install-types --non-interactive
	python -m mypy . --ignore-missing-imports
docu:
	pip install -e .
	python docs/source/update_index.py
	sphinx-apidoc -o docs/source soupsavvy --separate --force
	python docs/source/renaming.py -- docs/source
	rm -rf build_/
	sphinx-build docs/source build_/
	git clean -fd docs/source/*.rst
