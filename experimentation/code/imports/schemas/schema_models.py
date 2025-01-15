from typing import Any, Callable, Dict, List, Optional, Type, Union

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

class StringOptionalModel(BaseModel):
    items: Optional[str]

class DictOptionalModel(BaseModel):
    items: Optional[Dict[str, str]]

class Examples(BaseModel):
    # note: the = sign here doest mean default assignment, its a bit weird syntax i know
    items: Optional[List[Dict[str, str]]] = \
    Field(description="Description of the attribute") 

class ToolDocs_Summary_RequiredParameters_Parameter(BaseModel):
    name: str = Field(description="Description of the attribute")
    type: str = Field(description="Description of the attribute")
    description: str = Field(description="Description of the attribute")

class ToolDocs_Summary_OptionalConfigParameters_Parameter(BaseModel):
    name: str = Field(description="Description of the attribute")
    type: str = Field(description="Description of the attribute")
    description: str = Field(description="Description of the attribute")

class ToolDocs_Summary(BaseModel):
    what_you_want_to_do: str = Field(description="Description of the attribute")
    how_to_do_it: str = Field(description="Description of the attribute")
    required_parameters: List[ToolDocs_Summary_RequiredParameters_Parameter] = \
        Field(description="Description of the attribute")
    optional_config_parameters: \
        List[ToolDocs_Summary_OptionalConfigParameters_Parameter] = \
        Field(description="Description of the attribute")

class ToolDocs_Example(BaseModel):
    situation: str = Field(description="Description of the attribute")
    tool_use_in_english: str = Field(description="Description of the attribute")
    tool_use: str = Field(description="Description of the attribute")
    parameters_choice_explanation: str = \
        Field(description="Description of the attribute")
    exceptions_to_the_parameters_choice_explanation: str = \
        Field(description="Description of the attribute")

class ToolDocs(BaseModel):
    summary_of_the_tool: ToolDocs_Summary = \
        Field(description="Description of the attribute")
    examples_of_the_tool_being_used: List[ToolDocs_Example] = \
        Field(description="Description of the attribute")

class Tool(BaseModel):
    name: str = Field(description="Description of the attribute")
    docs: ToolDocs = Field(description="Description of the attribute")
    function_signature: str = Field(description="Description of the attribute")
    
class Tools(BaseModel):
    tools: List[Tool] = Field(description="Description of the attribute")

class ToolsOptional(BaseModel):
    tools: Optional[Tools] = Field(description="Description of the attribute")

class CompletionFormat(BaseModel):
    completion_format: Type[BaseModel] = \
    Field(description="Description of the attribute")

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
    completion_format: Type[BaseModel] = \
        Field(description="Description of the attribute")
 
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
    choices: List[LmChatResponse_Choice] = \
        Field(description="Description of the attribute")
    usage: LmChatResponse_Usage = Field(description="Description of the attribute")

class CompletionReasoning(BaseModel):
    reasoning_traces: str = Field(description="Description of the attribute")
    final_answer: str = Field(description="Description of the attribute")

class Message(BaseModel):
    role: str = Field(description="Description of the attribute")
    content: Union[Callable, str] = Field(description="Description of the attribute")

class MessageImage(BaseModel):
    role: str = Field(description="Description of the attribute")
    content: List[Dict[str, Any]] = Field(description="Description of the attribute")

class Messages(BaseModel):
    messages: List[Union[Message, MessageImage]] = \
    Field(description="Description of the attribute")

class LmChatResponseReconstruct_Message(BaseModel):
    role: str = Field(description="Description of the attribute")
    parsed: Any = Dict[str, Any]
    completion_format: Type[BaseModel] = \
        Field(description="Description of the attribute")

class LmChatResponseReconstruct_Choice(BaseModel):
    index: int = Field(description="Description of the attribute")
    message: LmChatResponseReconstruct_Message = \
    Field(description="Description of the attribute")
    finish_reason: str = Field(description="Description of the attribute")

class LmChatResponseReconstruct_Usage_CompletionTokensDetails(BaseModel):
    reasoning_tokens: int = Field(description="Description of the attribute")
    accepted_prediction_tokens: int = Field(description="Description of the attribute")
    rejected_prediction_tokens: int = Field(description="Description of the attribute")

class LmChatResponseReconstruct_Usage(BaseModel):
    prompt_tokens: int = Field(description="Description of the attribute")
    completion_tokens: int = Field(description="Description of the attribute")
    total_tokens: int = Field(description="Description of the attribute")
    completion_tokens_details: LmChatResponseReconstruct_Usage_CompletionTokensDetails

class LmChatResponseReconstruct(BaseModel):
    created: int = Field(description="Description of the attribute")
    model: str = Field(description="Description of the attribute")
    object: str = Field(description="Description of the attribute")
    choices: List[LmChatResponseReconstruct_Choice] = \
        Field(description="Description of the attribute")
    usage: LmChatResponseReconstruct_Usage = \
        Field(description="Description of the attribute")

class CallStats(BaseModel):
    model_name: str = Field(description="Description of the attribute")
    temperature: Optional[float] = Field(description="Description of the attribute")
    tools: Optional[Tools] = Field(description="Description of the attribute")
    completion_format: Type[BaseModel]  = \
        Field(description="Description of the attribute")
    instruction: str = Field(description="Description of the attribute")
    backstory: str = Field(description="Description of the attribute")
    tips: Optional[str] = Field(description="Description of the attribute")
    image: Optional[str] = Field(description="Description of the attribute")
    image_format: Optional[Dict[str, str]] = \
        Field(description="Description of the attribute")
    image_examples: Optional[List[Dict[str, str]]] = \
        Field(description="Description of the attribute")
    examples: Optional[List[Dict[str, str]]] = \
        Field(description="Description of the attribute")
    constraints: Optional[str] = Field(description="Description of the attribute")

    response: LmChatResponseReconstruct = \
    Field(description="Description of the attribute")
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