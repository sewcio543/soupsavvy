.PHONY: build

build:
	python -m build
	twine check dist/*
setup:
	python -m pip install -r requirements.txt
	python -m pip install -r config/requirements_dev.txt
install:
	python -m pip install -e .
	python -m pip show soupsavvy
lint:
	python -m flake8 --config tox.ini
format:
	black . --line-length 88 --diff --check
test:
	python -m pytest -v -ra
coverage:
	python -m coverage run -m pytest
	python -m coverage report
	python -m coverage html
