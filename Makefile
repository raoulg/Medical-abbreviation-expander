GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

.PHONY: run clean distclean preproc build-preproc run-preproc serve up stop build-train run-train tail check-lfs

.DEFAULT: help

help:
	@echo "Usage: make [target]"
	@echo "make run"
	@echo "		installs the environment, lint the code, preprocess/train and serve the gui"
	@echo "make install"
	@echo "		when the requirements.txt file exists/has changed, this will update the requirements"
	@echo "make clean"
	@echo "		Removes pip dependencies and processed files"
	@echo "make distclean"
	@echo "		Removes the full environment"
	@echo "make preproc"
	@echo "		Runs the preprocessing pipeline using Docker"
	@echo "make serve"
	@echo "		Uses docker-compose to build a network with the api, gui and inference containers"
	@echo "make up"
	@echo "		After make serve (or make run), this is a fast way to spin up the gui"
	@echo "make stop"
	@echo "		stops the server"
	@echo "make train"
	@echo "		Trains the network on preprocessed data"
	@echo "make lint"
	@echo "		lints the code"
	@echo "make format"
	@echo "		formats the code"
	@echo "make tail"
	@echo "		Show tail of the docker-compose logs"
	@echo "make big"
	@echo "		For stress-testing, makes the corpus.txt file 100_000 times as big"
	@echo "make download-model"
	@echo "		Downloads the pretrained MedRoBERTa from huggingface"

run: install download-model format lint preproc train serve
	@echo "$(GREEN)Finished running the pipeline$(NC)"

VENV := env
REQUIREMENTS := requirements.txt
$(VENV)/bin/activate:
	@echo "$(GREEN)Creating virtual environment$(NC)"
	python -m venv $(VENV)

install: $(VENV)/bin/activate $(REQUIREMENTS)
	@echo "$(GREEN)Installing dependencies$(NC)"
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(REQUIREMENTS)
	@echo "$(GREEN)Finished installing dependencies$(NC)"

clean:
	@echo "$(RED)Removing installed dependencies$(NC)"
	$(VENV)/bin/pip freeze | xargs $(VENV)/bin/pip uninstall -y
	@echo "$(GREEN)Finished removing installed dependencies$(NC)"
	@echo "$(RED)Removing all processed files in assets/processed$(NC)"
	find assets/processed -not -name .gitkeep -delete
	\rm -f assets/raw/big_corpus.txt
	\rm -rf assets/model/models--CLTL--MedRoBERTa.nl


distclean:
	@echo "$(RED)Removing virtual environment$(NC)"
	\rm -rf $(VENV)
	@echo "$(GREEN)Finished removing virtual environment$(NC)"

preproc: build-preproc run-preproc
	@echo "$(GREEN)Finished preprocessing the data$(NC)"

build-preproc:
	@echo "$(GREEN)Building the preprocessing container$(NC)"
	docker build -t abbrev:preprocess -f ./pipeline/preprocess/preproc.Dockerfile .
	@echo "$(GREEN)Finished building the preprocessing container$(NC)"

run-preproc:
	@echo "$(GREEN)Running the preprocessing container$(NC)"
	docker run --rm -v $(CURDIR)/assets:/app/assets abbrev:preprocess --project=. process.jl
	@echo "$(GREEN)Finished running the preprocessing container$(NC)"

serve:
	@echo "$(GREEN)Starting the pipeline server$(NC)"
	docker-compose -f pipeline/docker-compose.yml up --build -d
	@echo "$(GREEN)Please wait a few seconds while the service is starting. You can then access it at http://localhost:8501$(NC)"
	@echo "$(GREEN)Access logs with make tail, and stop the service with make stop"

up:
	@echo "$(GREEN)Starting the pipeline server$(NC)"
	docker-compose -f pipeline/docker-compose.yml up -d
	@echo "$(GREEN)Please wait a few seconds while the service is starting. You can then access it at http://localhost:8501$(NC)"

stop:
	@echo "$(RED)Stopping the pipeline server...$(NC)"
	docker-compose -f pipeline/docker-compose.yml down
	@echo "$(GREEN)Finished stopping the server$(NC)"

train: build-train run-train
	@echo "$(GREEN)Finished training$(NC)"

build-train:
	@echo "$(GREEN)building the trainimage$(NC)"
	docker build -f pipeline/train/train.Dockerfile -t train:latest .

run-train:
	docker run --rm \
		-v $(CURDIR)/assets:/app/assets \
		-v $(CURDIR)/pipeline/logs:/app/logs \
		-v $(CURDIR)/artefacts/mlflow:/app/mlflow train:latest

lint: $(VENV)/bin/activate
	@echo "$(GREEN)Linting the code$(NC)"
	$(VENV)/bin/flake8 pipeline
	$(VENV)/bin/mypy --no-strict-optional --warn-unreachable --show-error-codes --ignore-missing-imports pipeline/api
	$(VENV)/bin/mypy --no-strict-optional --warn-unreachable --show-error-codes --ignore-missing-imports pipeline/gui
	$(VENV)/bin/mypy --no-strict-optional --warn-unreachable --show-error-codes --ignore-missing-imports pipeline/train
	@echo "$(GREEN)Finished linting the code$(NC)"

format: $(VENV)/bin/activate
	@echo "$(GREEN)Formatting the code$(NC)"
	$(VENV)/bin/isort -v pipeline
	$(VENV)/bin/black pipeline
	@echo "$(GREEN)Finished formatting the code$(NC)"

tail:
	@echo "$(GREEN) Tailing logs...$(NC)"
	docker-compose -f pipeline/docker-compose.yml logs

big_corpus.txt: assets/raw/corpus.txt
	@echo "$(GREEN)Generating big_corpus.txt...$(NC)"
	cat $< > $@
	for i in {1..100000}; do cat $< >> $@; done
	@echo "$(GREEN)Done generating big_corpus.txt.$(NC)"

big: big_corpus.txt
	@echo "$(GREEN)Build complete.$(NC)"

check-lfs:
	@if ! git lfs env >/dev/null 2>&1; then \
		echo "Git LFS is not installed. Please install for your system"; \
		exit 1; \
	fi

download-model: check-lfs
	@echo "$(GREEN)Downloading MedRoBERTa.nl model...$(NC)"
	@if [ -d "assets/model/models--CLTL--MedRoBERTa.nl" ]; then \
		cd assets/model/models--CLTL--MedRoBERTa.nl && git pull; \
	else \
		git clone https://huggingface.co/CLTL/MedRoBERTa.nl.git assets/model/models--CLTL--MedRoBERTa.nl; \
	fi

