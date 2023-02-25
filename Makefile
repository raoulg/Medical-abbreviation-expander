GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

.PHONY: run install clean distclean preproc build-preproc run-preproc serve-pipeline up train lint format

.DEFAULT: run

run: install format preproc serve-pipeline
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
	@echo "$(GREEN)Removing installed dependencies$(NC)"
	$(VENV)/bin/pip freeze | xargs $(VENV)/bin/pip uninstall -y
	@echo "$(GREEN)Finished removing installed dependencies$(NC)"

distclean:
	@echo "$(GREEN)Removing virtual environment$(NC)"
	rm -rf $(VENV)
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

serve-pipeline:
	@echo "$(GREEN)Starting the pipeline server$(NC)"
	docker-compose -f pipeline/docker-compose.yml up --build
	@echo "$(GREEN)Finished running the pipeline server$(NC)"

up:
	@echo "$(GREEN)Starting the pipeline server$(NC)"
	docker-compose -f pipeline/docker-compose.yml up
	@echo "$(GREEN)Finished running the pipeline server$(NC)"

train:
	@echo "$(GREEN)Training the model$(NC)"
	# command to train the model goes here
	@echo "$(GREEN)Finished training the model$(NC)"

lint: $(VENV)/bin/activate
	@echo "$(GREEN)Linting the code$(NC)"
	$(VENV)/bin/flake8 pipeline
	$(VENV)/bin/mypy --no-strict-optional --warn-unreachable --show-error-codes --ignore-missing-imports pipeline
	@echo "$(GREEN)Finished linting the code$(NC)"

format: $(VENV)/bin/activate
	@echo "$(GREEN)Formatting the code$(NC)"
	$(VENV)/bin/black pipeline
	$(VENV)/bin/isort -v pipeline
	@echo "$(GREEN)Finished formatting the code$(NC)"