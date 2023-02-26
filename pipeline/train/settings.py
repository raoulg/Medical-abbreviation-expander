from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    modelpath: str
    hidden: int
    aggtype: str
    nonlinear: str


class FileSettings(BaseModel):
    bucket: str
    datadir: Path
    processed: Path
    mappingsuffix: str
    datasuffix: str
    sep: str

class DataSettings(BaseModel):
    targetcol : str
    txtcol: str



root = (Path(__file__).parent / "../..").resolve()

filesettings = FileSettings(
    bucket="",
    datadir=root / "assets",
    processed=root / "assets/processed/",
    mappingsuffix=".json",
    datasuffix=".csv",
    sep="|",
)

modelsettings = Settings(
    modelpath="CLTL/MedRoBERTa.nl",
    hidden=128,
    aggtype="mean",
    nonlinear="GRN",
)

datasettings = DataSettings(
    targetcol = "label",
    txtcol = "txt"
)