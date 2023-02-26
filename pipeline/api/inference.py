from collections import defaultdict
from typing import Dict, Type

import torch
from data import FileHandler
from layers import AbbrvtExpander
from settings import filesettings


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
