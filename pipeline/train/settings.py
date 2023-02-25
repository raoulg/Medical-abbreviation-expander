from pydantic import BaseModel


class Settings(BaseModel):
    modelpath: str = "CLTL/MedRoBERTa.nl"
    hidden: int = 128
    aggtype: str = "mean"
    nonlinear: str = "GRN"
