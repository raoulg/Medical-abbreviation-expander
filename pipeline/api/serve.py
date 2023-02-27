from pathlib import Path
from typing import Dict

import api_config as cfg
import torch
from fastapi import FastAPI
from inference import check_model, expand_abbreviation, get_invert_mapping
from loguru import logger

app = FastAPI()

loaded_model = None
inverted_dict = get_invert_mapping()


@app.get("/expand_sentence")
async def expand_sentence(sentence: str) -> Dict:
    global loaded_model
    modelpath = f"{cfg.MODELDIR}/{cfg.MODELVERSION}trainedmodel.pt"

    modelpath = str(check_model(Path(modelpath)))
    logger.info(f"using {modelpath}")

    if loaded_model is None:
        # lazy loading the model
        loaded_model = torch.load(modelpath, map_location=torch.device("cpu"))
    expanded_sentence = expand_abbreviation(sentence, inverted_dict, loaded_model)

    return {"expanded_sentence": expanded_sentence}
