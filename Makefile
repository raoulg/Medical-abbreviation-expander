.PHONY: run install clean distclean preproc build-preproc run-preproc serve-pipeline up train lint format

.DEFAULT: run

run: install format preproc serve-pipeline

VENV := env
REQUIREMENTS := requirements.txt

# Create the virtual environment if it doesn't exist yet
$(VENV)/bin/activate:
	python -m venv $(VENV)

# Install the dependencies and create the virtual environment if necessary
install: $(VENV)/bin/activate $(REQUIREMENTS)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(REQUIREMENTS)

# Remove the installed dependencies, but keep the virtual environment
clean:
	$(VENV)/bin/pip freeze | xargs $(VENV)/bin/pip uninstall -y
	@echo "Cleaned up installed dependencies"

# Remove the virtual environment and installed dependencies
distclean:
	rm -rf $(VENV)
	@echo "Removed virtual environment"

preproc: build-preproc run-preproc

build-preproc:
	docker build -t abbrev:preprocess -f ./pipeline/preprocess/preproc.Dockerfile .

run-preproc:
	docker run --rm -v $(CURDIR)/assets:/app/assets abbrev:preprocess --project=. process.jl

serve-pipeline:
	docker-compose -f pipeline/docker-compose.yml up --build

up:
	docker-compose -f pipeline/docker-compose.yml up

train:

lint: $(VENV)/bin/activate
	$(VENV)/bin/flake8 pipeline
	$(VENV)/bin/mypy --no-strict-optional --warn-unreachable --show-error-codes --ignore-missing-imports pipeline


format: $(VENV)/bin/activate
	$(VENV)/bin/black pipeline
	$(VENV)/bin/isort -v pipeline