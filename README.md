# Intro
Much clinical information is recorded in free-text medical reports which usually contain a large number of abbreviations. Some of these abbreviations may be ambiguous therefore it is crucial for an EHR parser to be able to infer to the correct expansion from the context.
This pipeline is an attempt at a production-ready solution to disambiguate acronyms using machine learning.
• Given a text containing acronyms, the code has to determine for each acronym which of its possible expansions it refers to.
• There is code for training and for inference
• The code works for the acronyms provided in the toy dataset (test_set.csv), but the solution
allows the extension to a much larger set of acronyms. This would require retraining of course, but no change in the code is required.

# data
• test_set.csv contains abbreviations with possible expansions with some example sentences. Since there are multiple examples per acronym-expansion combination it can be used as a small test set. It is a pipe separated file, and the explanation of the columns is as follows:
o Acronym: The acronym (will appear multiple times because there are multiple expansions)
o Expansion: The expansion of the acronym
o Type: The conceptual category that the expansion belongs to (this is not needed for
the NLP task, but is part of the dataset as we have it)
o Sample: An example of the acronym in a typical sentence

• corpus.txt contains unannotated sentences in which the above terms appear. They can be considered an equivalent of the textual data that is available in a hospital to work with. In a real setting this data would be in the order of millions.

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
