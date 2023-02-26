import json
from pathlib import Path
from typing import Dict, Iterator, Tuple

from settings import FileSettings


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
        """This is a mapping from expansions to possible abbreviations.
        The mapping from expansions to abbreviations is
            - surjective (every expansion is mapped to at least one abbreviation)
            - non-injective (meaning that it is not the case that there is a one-to-one
                relation where every expansion is mapped to at most one abbreviation)
        The filepath is a json file, which is flattened to a dict.
        This flattening assumes there are NEVER expansions mapping to
        more than one abbreviation

        Args:
            filepath (Path): json file with the mapping

        Returns:
            Dict
        """
        with open(filepath, "r") as f:
            data = json.load(f)
        result = {}

        # this flattening assumes there are never expansions mapping
        # to more than one abbreviation
        for item in data:
            for key, value in item.items():
                result[key] = value
        return result
