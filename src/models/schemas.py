"""
ARA - Pydantic Models & Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class IntentType(str, Enum):
    REALITY = "Reality"
    DECISION = "Decision"
    OPTIMIZATION = "Optimization"
    INNOVATION = "Innovation"


class DepthLevel(str, Enum):
    LEVEL_0 = "Level0"
    LEVEL_1 = "Level1"
    LEVEL_2 = "Level2"
    LEVEL_3 = "Level3"


class IntentResult(BaseModel):
    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)


class DepthResult(BaseModel):
    depth: DepthLevel
    reason: str


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    code: int = 0
    data: dict
    message: str = "ok"


class HealthResponse(BaseModel):
    status: str = "ok"


class MetricsResponse(BaseModel):
    total_requests: int = 0
    active_conversations: int = 0
    avg_response_time_ms: float = 0.0


# Export models
class ExportPdfRequest(BaseModel):
    title: str
    content: str
    intent: str = "Reality"
    depth: str = "Level1"
    word_range: str = "300~800字"


class ExportNotionRequest(BaseModel):
    title: str
    content: str
    parent_page_id: Optional[str] = None


class ExportResponse(BaseModel):
    code: int = 0
    data: dict
    message: str = "ok"
