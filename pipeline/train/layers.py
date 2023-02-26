from typing import List, Tuple

import torch
import torch.nn.functional as F  # noqa N812
from settings import Settings
from torch import nn
from transformers import RobertaModel, RobertaTokenizer


class Vectorizer(nn.Module):
    def __init__(self, modelsettings: Settings) -> None:
        super().__init__()
        self.hidden: int = modelsettings.hidden
        self.model_path = modelsettings.modelpath

        self.roberta = RobertaModel.from_pretrained(
            self.model_path,
            output_hidden_states=False,
            cache_dir=modelsettings.cache_dir,
        )
        self.tokenizer = RobertaTokenizer.from_pretrained(
            self.model_path, cache_dir=modelsettings.cache_dir
        )
        self.vectordim = modelsettings.vectordim
        self.hidden = modelsettings.hidden

        self.aggtype = modelsettings.aggtype
        self.nonlinear = modelsettings.nonlinear
        self.reducer = nn.Sequential(
            nn.Linear(modelsettings.vectordim, 2 * self.hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(2 * self.hidden, self.hidden),
        )
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


class AbbrvtExpander(Vectorizer):
    def stacked_vectorize(self, y_: List[Tuple[str]]) -> torch.Tensor:
        m = []
        for val in y_:
            m.append(self.vectorize(val))
        return torch.stack(m)

    def vectorize(self, batch: Tuple[str]) -> torch.Tensor:
        inputs = self.tokenizer.batch_encode_plus(
            batch,
            return_tensors="pt",
            padding=True,
        )["input_ids"]
        vector = self.roberta(inputs).last_hidden_state
        vector = self._agg(vector)
        vector = self.reducer(vector)
        return vector

    def cosine_sim(
        self, context: torch.Tensor, candidates: torch.Tensor
    ) -> torch.Tensor:
        return F.cosine_similarity(context.unsqueeze(1), candidates, dim=-1)

    def forward(self, X: Tuple[str], y_: List[Tuple[str]]) -> torch.Tensor:  # noqa N803
        context = self.vectorize(X)
        candidates = self.stacked_vectorize(y_)
        yhat = self.cosine_sim(context, candidates)
        return yhat
