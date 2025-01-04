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
    submitted_instances: int
    resolved_instances: int
    skipped_instances: int

class Metrics(BaseModel):
    percentage_resolved: float
    kowinski_score: float