from typing import Any, List

import pandas as pd
from pydantic import BaseModel, validator


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

class PandasSeriesModel(BaseModel):
    series: Any

    @validator('series')
    def check_series(cls, value):
        if not isinstance(value, pd.Series):
            raise ValueError('The value must be a pandas Series')
        return value

class PandasDataFrameModel(BaseModel):
    dataframe: Any

    @validator('dataframe')
    def check_dataframe(cls, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError('The value must be a pandas DataFrame')
        return value