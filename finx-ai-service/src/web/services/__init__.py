from datetime import datetime
from typing import Literal, Optional

import orjson
import pytz
from pydantic import AliasChoices, BaseModel, Field


class Configuration(BaseModel):
    class Timezone(BaseModel):
        name: str = "UTC"
        utc_offset: str = ""  # Deprecated, will be removed in the future

    def show_current_time(self):
        # Get the current time in the specified timezone
        tz = pytz.timezone(
            self.timezone.name
        )  # Assuming timezone.name contains the timezone string
        current_time = datetime.now(tz)

        return f"{current_time.strftime('%Y-%m-%d %A %H:%M:%S')}"  # YYYY-MM-DD weekday_name HH:MM:SS, ex: 2024-10-23 Wednesday 12:00:00

    language: str = "English"
    timezone: Timezone = Timezone()


class BaseRequest(BaseModel):
    _query_id: str | None = None
    project_id: Optional[str] = None
    thread_id: Optional[str] = None
    configurations: Configuration = Field(
        default_factory=Configuration,
        alias=AliasChoices("configurations", "configuration"),  # accept both keys
    )
    request_from: Literal["ui", "api"] = "ui"

    @property
    def query_id(self) -> str:
        return self._query_id

    @query_id.setter
    def query_id(self, query_id: str):
        self._query_id = query_id


class SSEEvent(BaseModel):
    class SSEEventMessage(BaseModel):
        message: str

        def to_dict(self):
            return {"message": self.message}

    data: SSEEventMessage

    def serialize(self):
        return f"data: {orjson.dumps(self.data.to_dict()).decode()}\n\n"


# Import services
from .ask import (
    AskService,
    AskRequest,
    AskResponse,
    AskResult,
    AskResultResponse,
    AskError,
    AskHistory,
    StopAskResponse,
)
from .question_recommendation import (
    QuestionRecommendationService,
    QuestionRecommendationRequest,
    QuestionRecommendationResponse,
    QuestionRecommendationResult,
    RecommendedQuestion,
)

__all__ = [
    # Base classes
    "Configuration",
    "BaseRequest",
    "SSEEvent",
    # Ask service
    "AskService",
    "AskRequest",
    "AskResponse",
    "AskResult",
    "AskResultResponse",
    "AskError",
    "AskHistory",
    "StopAskResponse",
    # Question recommendation service
    "QuestionRecommendationService",
    "QuestionRecommendationRequest",
    "QuestionRecommendationResponse",
    "QuestionRecommendationResult",
    "RecommendedQuestion",
]