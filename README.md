# dependencies
The pipeline needs `docker` and `docker-compose` to run.

For linting and formating, the `make environment` command will install a local python environment in a `env` folder if it does not exist yet, which is used for linting and formatting.

# running the pipeline
## preprocess
`make preproc` will run 
- `build-preproc`that builds the preproc container
- `run-preproc` that will run the container

After the preprocessing is done, the files inside `assets/raw` are processed and stored into `assets/processed`

## Serve
`make serve-pipeline` will start the `docker-compose.yml` network, that contains
- a fastapi endpoint
- a basic gui with streamlit to interact with the api
- a trainstep that trains and stores the model

running `make` defaults to building the environment, preprocessing the files in the `assets/raw` folder and starting up the training pipeline and serve the api/gui.

The gui can be found at `http://localhost:8501/`

After the environment has been built, you can start up the network with `make up`

