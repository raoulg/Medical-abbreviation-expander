from collections import defaultdict
from pathlib import Path
from typing import Dict, Type

import api_config as cfg
import torch
from data import FileHandler, walk_dir
from layers import AbbrvtExpander
from loguru import logger
from settings import filesettings, filetypes


def check_model(modelpath: Path) -> Path:
    if not modelpath.exists():
        logger.warning(
            f"You tried to load {modelpath} from {cfg.MODELDIR}, but it does not exist"
        )
        logger.info(
            "Obtain the model, or change the modelversion in the api_config.py file"
        )
        files = walk_dir(Path(cfg.MODELDIR))
        models = [p for p in files if p.suffix == filetypes.PYTORCHMODEL]
        if len(models) == 0:
            logger.error(f"There are no other models in {cfg.MODELDIR}")
        else:
            modelpath = sorted(models, reverse=True)[0]
            logger.warning(f"Found latest model {modelpath}, using that")
    else:
        logger.info(f"Found model {modelpath}")

    return modelpath


def get_invert_mapping() -> Dict:
    filehandler = FileHandler(filesettings)
    mappath, _ = filehandler._get_latest()
    mapping = filehandler.load_mapping(mappath)
    inverted_dict = defaultdict(list)
    for key, value in mapping.items():
        inverted_dict[value].append(key)
    return inverted_dict


def expand_abbreviation(
    sentence: str, inverted_dict: Dict, model: Type[AbbrvtExpander]  # type: ignore
) -> str:
    abbreviations = [key for key in inverted_dict.keys() if key in sentence]
    for abbr in abbreviations:
        candidates = inverted_dict[abbr]
        print(candidates)
        candidates = [tuple(candidates)]
        s = (
            sentence,
            sentence,
        )  # this avoids pytorch collapsing the singleton dimension
        yhat = model(s, candidates)  # type: ignore
        idx = torch.argmax(yhat, dim=1)[0]  # type: ignore
        expansion = candidates[0][idx]
        sentence = sentence.replace(abbr, expansion)
    return sentence
