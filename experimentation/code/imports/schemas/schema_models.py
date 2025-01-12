from typing import Any, Callable, List, Optional, Type, Union

import pandas as pd
from pydantic import BaseModel, Field, validator


class StringModel(BaseModel):
    items: str

class IntModel(BaseModel):
    items: int

class FloatModel(BaseModel):
    items: float

class BoolModel(BaseModel):
    items: bool

class StringListModel(BaseModel):
    items: List[str]

class Tool(BaseModel):
    name: str = Field(description="Description of the attribute")
    description: str = Field(description="Description of the attribute")
    function_signature: str = Field(description="Description of the attribute")
    
class Tools(BaseModel):
    tools: List[Tool] = Field(description="Description of the attribute")

class ToolsOptional(BaseModel):
    tools: Optional[Tools] = Field(description="Description of the attribute")

class CompletionFormat(BaseModel):
    completion_format: Type[BaseModel] = Field(description="Description of the attribute")

class RelevantSubResults(BaseModel):
    num_submitted_instances: int = Field(description="Description of the attribute")
    num_resolved_instances: int = Field(description="Description of the attribute")
    num_skipped_instances: int = Field(description="Description of the attribute")

class Metrics(BaseModel):
    percentage_resolved: float = Field(description="Description of the attribute")
    kowinski_score: float = Field(description="Description of the attribute")

class PandasSeriesModel(BaseModel):
    series: Any

    @validator('series')
    def check_series(cls, value):
        if not isinstance(value, pd.Series):
            raise TypeError('The value must be a pandas Series')
        return value

class LmChatResponse_Message(BaseModel):
    role: str = Field(description="Description of the attribute")
    parsed: Any = Field(description="Description of the attribute")
    completion_format: Type[BaseModel] = Field(description="Description of the attribute")
 
    @validator('parsed')
    def check_content(cls, value):
        if not isinstance(value, BaseModel):
            raise TypeError('The value must be an instance of BaseModel')
        return value

class LmChatResponse_Choice(BaseModel):
    index: int = Field(description="Description of the attribute")
    message: LmChatResponse_Message = Field(description="Description of the attribute")
    finish_reason: str = Field(description="Description of the attribute")

class LmChatResponse_Usage_CompletionTokensDetails(BaseModel):
    reasoning_tokens: int = Field(description="Description of the attribute")
    accepted_prediction_tokens: int = Field(description="Description of the attribute")
    rejected_prediction_tokens: int = Field(description="Description of the attribute")

class LmChatResponse_Usage(BaseModel):
    prompt_tokens: int = Field(description="Description of the attribute")
    completion_tokens: int = Field(description="Description of the attribute")
    total_tokens: int = Field(description="Description of the attribute")
    completion_tokens_details: LmChatResponse_Usage_CompletionTokensDetails

class LmChatResponse(BaseModel):
    created: int = Field(description="Description of the attribute")
    model: str = Field(description="Description of the attribute")
    object: str = Field(description="Description of the attribute")
    choices: List[LmChatResponse_Choice] = Field(description="Description of the attribute")
    usage: LmChatResponse_Usage = Field(description="Description of the attribute")

class CompletionReasoning(BaseModel):
    reasoning_traces: str = Field(description="Description of the attribute")
    final_answer: str = Field(description="Description of the attribute")

class Message(BaseModel):
    role: str = Field(description="Description of the attribute")
    content: Union[Callable, str] = Field(description="Description of the attribute")

class CallStats(BaseModel):
   mode: Optional[str] = Field(description="Description of the attribute")
   response: LmChatResponse = Field(description="Description of the attribute")
   cost: float = Field(description="Description of the attribute")
   duration: float = Field(description="Description of the attribute")

class State(BaseModel):
    number_of_calls_made: int = Field(description="Description of the attribute")
    total_cost: float = Field(description="Description of the attribute")
    total_time: float = Field(description="Description of the attribute")
    average_cost_per_call: float = Field(description="Description of the attribute")
    average_time_per_call: float = Field(description="Description of the attribute")

class LmSummary(BaseModel):
    history: List[CallStats]
    state: State

# --- For custom validators ----

def ValidateRelevantSubResults(item):
    if not isinstance(item, RelevantSubResults):
        raise TypeError(f"{item} is not a valid RelevantSubResults object")

def ValidateMetrics(item):
    if not isinstance(item, Metrics):
        raise TypeError(f"{item} is not a valid Metrics object")

def ValidateLmSummary(item):
    if not isinstance(item, LmSummary):
        raise TypeError(f"{item} is not a valid LmSummary object")

def ValidateLmChatResponse(item):
    if not isinstance(item, LmChatResponse):
        raise TypeError(f"{item} is not a valid LmChatResponse object")