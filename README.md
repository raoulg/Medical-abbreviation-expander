# dependencies
The pipeline needs `docker` and `docker-compose` to run.

# running the pipeline
running `make` shows the help for the makefile.
The complete pipeline will be built with `make run`, which:
- builds the environment
- downloads the huggingface model
- formats and lints the code
- preprocesses the data in assets/raw
- trains the model
- spins up the api and gui

The gui can be found at `http://localhost:8501/`

After the environment has been built, you can 
start up the server with `make up`