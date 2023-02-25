from fastapi import FastAPI

app = FastAPI()


@app.get("/expand_sentence")
async def expand_sentence(sentence: str):
    # Replace "lafe AF" with "lafe ademfrequentie"
    expanded_sentence = sentence.replace("AF", "ademfrequentie")
    return {"expanded_sentence": expanded_sentence}
