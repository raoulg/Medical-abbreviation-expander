import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterator, List, Sequence, Tuple

import numpy as np
import polars as pl
import torch
from loguru import logger
from settings import DataSettings, FileSettings


def walk_dir(path: Path) -> Iterator:
    """loops recursively through a folder

    Args:
        path (Path): folder to loop trough. If a directory
            is encountered, loop through that recursively.

    Yields:
        Generator: all paths in a folder and subdirs.
    """

    for p in Path(path).iterdir():
        if p.is_dir():
            yield from walk_dir(p)
            continue
        yield p.resolve()


class FileHandler:
    def __init__(self, settings: FileSettings) -> None:
        self.bucket = settings.bucket
        self.data_dir = settings.datadir
        self.processed = settings.processed
        self.mappingsuffix = settings.mappingsuffix
        self.datasuffix = settings.datasuffix
        self.sep = settings.sep

    def __repr__(self) -> str:
        return f"FileHandler(bucket='{self.bucket}', data_dir='{self.data_dir}')"

    def _get_latest(self) -> Tuple[Path, Path]:
        files = [*walk_dir(self.processed)]
        maps = [
            f for f in sorted(files, reverse=True) if f.suffix == self.mappingsuffix
        ][0]
        train = [f for f in sorted(files, reverse=True) if f.suffix == self.datasuffix][
            0
        ]
        return maps, train

    def load_mapping(self, filepath: Path) -> Dict:
        with open(filepath, "r") as f:
            data = json.load(f)
        result = {}
        for item in data:
            for key, value in item.items():
                result[key] = value
        return result

    def load_data(self, filepath: Path) -> pl.DataFrame:
        logger.info(f"loading file from {filepath}")
        try:
            if self.datasuffix == ".parq":
                data = pl.read_parquet(filepath)
            elif self.datasuffix == ".csv":
                data = pl.read_csv(filepath, sep=self.sep)
            else:
                raise ValueError("Unsupported file format")

        except (IOError, FileNotFoundError) as e:
            raise IOError(f"Failed to load file {filepath}") from e
        return data


class BaseDataset:
    """The main responsibility of the Dataset class is to load the data from disk
    and to offer a __len__ method and a __getitem__ method
    """

    def __init__(self, data: pl.DataFrame, settings: DataSettings) -> None:
        self.dataset: List = []
        self.settings = settings
        self.size = len(data)
        self.process_data(data)

    def process_data(self, data: pl.DataFrame) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, idx: int) -> Tuple:
        return self.dataset[idx]


class TxtDataset(BaseDataset):
    def process_data(self, data: pl.DataFrame) -> None:
        X = data[self.settings.txtcol].to_list()  # noqa N806
        y = data[self.settings.targetcol].to_list()
        self.dataset = [*zip(X, y)]


class Datastreamer:
    """This datastreamer wil never stop
    The dataset should have a:
        __len__ method
        __getitem__ method

    """

    def __init__(
        self,
        dataset: BaseDataset,
        batchsize: int,
        mapping: Dict,
    ) -> None:
        self.dataset = dataset
        self.batchsize = batchsize
        self.mapping = mapping
        self.surject = self._surjection(mapping)
        self.size = len(self.dataset)
        self.reset_index()

    def __len__(self) -> int:
        return int(len(self.dataset) / self.batchsize)

    def reset_index(self) -> None:
        self.index_list = np.random.permutation(self.size)
        self.index = 0

    def _surjection(self, mapping: Dict) -> Dict:
        inverted_dict = defaultdict(list)
        for key, value in mapping.items():
            inverted_dict[value].append(key)
        surject = {k: tuple(inverted_dict[v]) for k, v in mapping.items()}
        return surject

    def _preprocess(
        self, batch: Sequence[Tuple]
    ) -> Tuple[Tuple[str], List[Tuple[str]], torch.Tensor]:
        X, y = zip(*batch)  # noqa N806
        y_ = [self.surject[val] for val in y]
        indices = torch.tensor([y_[i].index(y[i]) for i in range(len(y))])
        return X, y_, indices

    def batchloop(self) -> Sequence[Tuple]:
        batch = []
        for _ in range(self.batchsize):
            x, y = self.dataset[int(self.index_list[self.index])]
            batch.append((x, y))
            self.index += 1
        return batch

    def stream(self) -> Iterator:
        while True:
            if self.index > (self.size - self.batchsize):
                self.reset_index()
            batch = self.batchloop()
            X, candidates, y = self._preprocess(batch)  # noqa N806
            yield X, candidates, y
