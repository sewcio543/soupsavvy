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
	bash docs/sphinx_run.sh
	git clean -fd docs/source/*.rst
run_demos:
	python -m pytest --nbmake -v demos/
