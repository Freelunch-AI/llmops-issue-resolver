from typing import Any, Callable, List, Optional, Type, Union

import pandas as pd
from pydantic import BaseModel, ValidationError, validator


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

class Arguments(BaseModel):
    items: List[dict]

class Tool(BaseModel):
    name: str
    description: str
    function_signature: str
    
class Tools(BaseModel):
    tools: List[Tool]

class ToolUse(BaseModel):
    name: str
    arguments: Arguments
    
class ToolsUse(BaseModel):
    tools: List[ToolUse]

class CompletionFormatDescription(BaseModel):
    completion_format: Type[BaseModel]
    description: str

class RelevantSubResults(BaseModel):
    num_submitted_instances: int
    num_resolved_instances: int
    num_skipped_instances: int

class Metrics(BaseModel):
    percentage_resolved: float
    kowinski_score: float

class PandasSeriesModel(BaseModel):
    series: Any

    @validator('series')
    def check_series(cls, value):
        if not isinstance(value, pd.Series):
            raise ValidationError('The value must be a pandas Series')
        return value

class LmChatResponse_Message(BaseModel):
    role: str
    content: str
    completion_format: Type[BaseModel]
    tool_calls: Tools

class LmChatResponse_Choice(BaseModel):
    index: int
    message: LmChatResponse_Message
    finish_reason: str

class LmChatResponse_Usage_PromptTokensDetails(BaseModel):
    cached_tokens: int

class LmChatResponse_Usage_CompletionTokensDetails(BaseModel):
    reasoning_tokens: int

class LmChatResponse_Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: LmChatResponse_Usage_PromptTokensDetails
    completion_tokens_details: LmChatResponse_Usage_CompletionTokensDetails

class LmChatResponse(BaseModel):
    created: int
    model: str
    choices: List[LmChatResponse_Choice]
    usage: LmChatResponse_Usage

class CompletionReasoning(BaseModel):
    reasoning_traces: str
    final_answer: str

class Message(BaseModel):
    role: str
    content: Union[Callable, str]

class CallStats(BaseModel):
   mode: Optional[str]
   response: LmChatResponse
   cost: float
   duration: float

class State(BaseModel):
    number_of_calls_made: int
    total_cost: float
    total_time: float
    average_cost_per_call: float
    average_time_per_call: float

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

def ValidatePydanticModel(item):
    if not issubclass(item, BaseModel):
        raise TypeError(f"{item} is not a valid Pydantic model")

def ValidateMessagesModel(items):
    if not all(isinstance(item, MessageModel) for item in items):
        raise TypeError(f"{items} is not a valid list of MessageModel objects")