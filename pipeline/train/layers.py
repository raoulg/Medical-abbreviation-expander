from typing import Tuple

import torch
from settings import Settings
from torch import nn
from transformers import RobertaModel, RobertaTokenizer


class Vectorizer(nn.Module):
    def __init__(self, modelsettings: Settings) -> None:
        super().__init__()
        self.hidden: int = modelsettings.hidden
        self.model_path = modelsettings.modelpath

        self.roberta = RobertaModel.from_pretrained(
            self.model_path, output_hidden_states=False
        )
        self.tokenizer = RobertaTokenizer.from_pretrained(self.model_path)
        self.hidden = modelsettings.hidden
        self.aggtype = modelsettings.aggtype
        self.nonlinear = modelsettings.nonlinear
        assert self.aggtype in [
            "mean",
            "sum",
            "none",
        ], "Aggregation type must be 'mean', 'sum' or 'none'"

        for param in self.roberta.parameters():
            param.requires_grad = False

    def _agg(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if self.aggtype == "mean":
            return torch.mean(hidden_states, dim=1).squeeze()
        if self.aggtype == "sum":
            return torch.mean(hidden_states, dim=1).squeeze()
        else:
            return hidden_states

    def _nonlinear(self, hidden_states: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError()

    def forward(self, batch: Tuple[str]) -> torch.Tensor:
        raise NotImplementedError()


class AbbrvtExpander(Vectorizer):
    def _nonlinear(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if self.nonlinear == "GNR":
            return hidden_states
        return hidden_states

    def forward(self, batch: Tuple[str]) -> torch.Tensor:
        inputs = self.tokenizer.batch_encode_plus(
            batch,
            return_tensors="pt",
            padding=True,
        )["input_ids"]
        vector = self.roberta(inputs).last_hidden_state
        vector = self._agg(vector)
        vector = self._nonlinear(vector)
        return vector
