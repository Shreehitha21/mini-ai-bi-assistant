from pydantic import BaseModel
from typing import Optional, Any, Dict, List

# What we expect to receive from the frontend
class AskRequest(BaseModel):
    question: str

# What we will send back to the frontend
class AskResponse(BaseModel):
    success: bool
    question: str
    intent: Optional[str] = None
    answer: Optional[str] = None
    supporting_data: Any = None
    sql_operation: Optional[str] = None
    limitations: List[str] = []
    error: Optional[str] = None