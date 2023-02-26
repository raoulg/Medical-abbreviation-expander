from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    modelpath: str
    vectordim: int
    hidden: int
    aggtype: str
    nonlinear: str
    epochs: int
    train_steps: int
    eval_steps: int
    learning_rate: float
    modeldir: Path
    cache_dir: Path


class FileSettings(BaseModel):
    bucket: str
    datadir: Path
    processed: Path
    mappingsuffix: str
    datasuffix: str
    sep: str


class DataSettings(BaseModel):
    targetcol: str
    txtcol: str
    trainfrac: float
    batchsize: int


class FileTypes(BaseModel):
    PARQUET: str = ".parq"
    CSV: str = ".csv"


filetypes = FileTypes()

root = (Path(__file__).parent / "../..").resolve()

filesettings = FileSettings(
    bucket="",
    datadir=Path("assets"),
    processed=Path("assets/processed/"),
    mappingsuffix=".json",
    datasuffix=".csv",
    sep="|",
)

modelsettings = Settings(
    modelpath="CLTL/MedRoBERTa.nl",
    vectordim=768,
    hidden=128,
    aggtype="mean",
    nonlinear="GRN",
    epochs=10,
    train_steps=10,
    eval_steps=10,
    learning_rate=1e-3,
    modeldir=Path("mlflow"),
    cache_dir=Path("assets/model"),
)

datasettings = DataSettings(
    targetcol="label", txtcol="txt", trainfrac=0.8, batchsize=32
)
