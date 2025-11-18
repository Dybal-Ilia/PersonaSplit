from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import BaseMessage
from uuid import uuid4


class ChatState(BaseModel):
    topic: str = Field(..., description="The topic provided by a user's input")
    debators: List[str]
    session_id: str
    history_patch: Optional[BaseMessage] = None
    last_speaker: str = None
    next_speaker:str = None
    judge_decision: Optional[BaseMessage] = None
    replices_counter: int = 0