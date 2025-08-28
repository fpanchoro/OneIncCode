import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

DEFAULT_STYLES = ["professional", "casual", "polite", "social-media"]


class RephraseRequest(BaseModel):
    input_text: str = Field(min_length=1, max_length=8000)
    styles: List[str] = Field(default_factory=lambda: DEFAULT_STYLES)
    request_id: Optional[str] = None

    def ensure_request_id(self) -> str:
        return self.request_id or str(uuid.uuid4())


class RephraseResponse(BaseModel):
    request_id: str
    results: Dict[str, str]


class CancelResponse(BaseModel):
    request_id: str
    cancelled: bool
