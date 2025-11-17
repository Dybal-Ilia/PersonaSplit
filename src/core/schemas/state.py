from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ChatState(BaseModel):
    topic: str = Field(..., description="The topic provided by a user's input")
    debators: List[str]
    history: Annotated[List[BaseMessage], add_messages] = []
    recent_history: List[BaseMessage] = []
    history_patch: Optional[BaseMessage] = None
    last_speaker: str = None
    next_speaker:str = None
    judge_decision: Optional[BaseMessage] = None
    replices_counter: int = 0