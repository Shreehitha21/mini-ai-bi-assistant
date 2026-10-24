from pydantic import BaseModel
from typing import Optional, Any, Dict, List

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    success: bool
    question: str
    intent: Optional[str] = None
    answer: Optional[str] = None
    supporting_data: Any = None
    sql_operation: Optional[str] = None
    limitations: List[str] = []
    error: Optional[str] = None