DOC_OUTPUT_DIR ?= doc/_build

.PHONY: doc tests

clean:
	@rm -rf build dist
	@rm -rf src/*.egg-info
	@find src \( -name '*.py[co]' -o -name '__pycache__' \) -delete
	@rm -rf doc/_build/*

install-dev: clean
	git init
	python -m pre_commit install
	python -m pre_commit autoupdate

tests:
	python -m pytest

qa:
	python -m ruff src
	python -m ruff format --check src

qa-fix:
	python -m ruff --fix src
	python -m ruff format src

doc:
	python -m sphinx.cmd.build -b html doc ${DOC_OUTPUT_DIR}

wheel:
	python -m pip wheel -w dist --no-deps .
