from typing import Any, List, Optional

import pandas as pd
from pydantic import BaseModel, validator


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

class RelevantSubResults(BaseModel):
    num_submitted_instances: int
    num_resolved_instances: int
    num_skipped_instances: int

class Metrics(BaseModel):
    percentage_resolved: float
    kowinski_score: float

class LmSummary(BaseModel):
    history: List[dict]
    state: dict

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

class LmChatResponse_Message(BaseModel):
    role: str
    content: str
    refusal: Optional[str]
    output_format: str

class LmChatResponse_Choice(BaseModel):
    index: int
    message: LmChatResponse_Message
    logprobs: Optional[str]
    finish_reason: str

class LmChatResponse_PromptTokensDetails(BaseModel):
    cached_tokens: int

class LmChatResponse_CompletionTokensDetails(BaseModel):
    reasoning_tokens: int
    accepted_prediction_tokens: int
    rejected_prediction_tokens: int

class LmChatResponse_Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: LmChatResponse_PromptTokensDetails
    completion_tokens_details: LmChatResponse_CompletionTokensDetails

class LmChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[LmChatResponse_Choice]
    usage: LmChatResponse_Usage
    system_fingerprint: str

class ExampleOutputModel(BaseModel):
    reasoning_traces: str
    final_answer: str

class MessageModel(BaseModel):
    role: str
    content: str

# --- For custom validators ----

class ValidateRelevantSubResults(BaseModel):
    relevant_subresults: RelevantSubResults

    @validator('relevant_subresults')
    def must_be_relevant_subresults(cls, value):
        if not isinstance(value, RelevantSubResults):
            raise ValueError('must be an instance of RelevantSubResults')
        return value
    
class ValidateMetrics(BaseModel):
    metrics: Metrics

    @validator('metrics')
    def must_be_metrics(cls, value):
        if not isinstance(value, Metrics):
            raise ValueError('must be an instance of Metrics')
        return value

class ValidateLmSummary(BaseModel):
    summary: LmSummary

    @validator('summary')
    def must_be_summary(cls, value):
        if not isinstance(value, LmSummary):
            raise ValueError('must be an instance of Summary')
        return value

class ValidateBaseModel(BaseModel):
    base_model: BaseModel

    @validator('base_model')
    def must_be_base_model(cls, value):
        if not isinstance(value, BaseModel):
            raise ValueError('must be an instance of BaseModel')
        return value
    
class ValidateLmChatResponse(BaseModel):
    lm_chat_response: LmChatResponse

    @validator('lm_chat_response')
    def must_be_lm_chat_response(cls, value):
        if not isinstance(value, LmChatResponse):
            raise ValueError('must be an instance of LmChatResponse')
        return value

class ValidateExampleOutputModel(BaseModel):
    example_output_model: ExampleOutputModel

    @validator('example_output_model')
    def must_be_example_output_model(cls, value):
        if not isinstance(value, ExampleOutputModel):
            raise ValueError('must be an instance of ExampleOutputModel')
        return value

class ValidateMessageModel(BaseModel):
    messages: List[MessageModel]

    @validator('messages')
    def must_be_message_model(cls, value):
        if not all(isinstance(item, MessageModel) for item in value):
            raise ValueError('all items must be instances of MessageModel')
        return value