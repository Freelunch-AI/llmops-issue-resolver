from typing import List

from pydantic import BaseModel


class StringModel(BaseModel):
    items: str

class IntModel(BaseModel):
    items: int

class BoolModel(BaseModel):
    items: bool

class StringListModel(BaseModel):
    items: List[str]

class RelevantSubResults(BaseModel):
    pass

class Metrics(BaseModel):
    pass