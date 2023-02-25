.DEFAULT: run

run:
	make environment
	make preproc
	#make train
	make serve-pipeline

# create and update the local environment
environment:
	test -d env || python -m venv env # will only run if env is not present
	make install

vendored-folder := env
install: $(vendored-folder)

$(vendored-folder): requirements.txt
	# only runs if the requirements.txt file has changed
	\rm -rf $(vendored-folder)  # the \ avoids using my local alias for rm
	pip install --upgrade pip
	pip install -r requirements.txt -t $(vendored-folder)

preproc:
	make build-preproc	
	make run-preproc

build-preproc:
	docker build -t abbrev:preprocess -f ./pipeline/preprocess/preproc.Dockerfile .

run-preproc:
	docker run --rm -v $$(pwd)/assets:/app/assets abbrev:preprocess --project=. process.jl

serve-pipeline:
	docker-compose -f pipeline/docker-compose.yml up --build

up:
	docker-compose -f pipeline/docker-compose.yml up

lint:
	flake8 pipeline
	mypy --no-strict-optional --warn-unreachable --show-error-codes --ignore-missing-imports pipeline

train:

format:
	isort -v pipeline
	black pipeline



