import torch
from typing import Dict
from fastapi import FastAPI
import api_config as cfg
from pathlib import Path

app = FastAPI()

loaded_model = None

@app.get("/expand_sentence")
async def expand_sentence(sentence: str) -> Dict:
    global loaded_model
    modelpath = f"{cfg.MODELDIR}/{cfg.MODELVERSION}trainedmodel.pt"


    print(modelpath)
    if loaded_model is None:
        print("loading model")
        loaded_model = torch.load(modelpath, map_location=torch.device('cpu'))

    expanded_sentence = sentence.replace("AF", "ademfrequentie")
    return {"expanded_sentence": expanded_sentence}
