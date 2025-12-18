from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field


class ChatState(BaseModel):
    topic: str = Field(..., description="The topic provided by a user's input")
    debators: list[str]
    session_id: str
    history_patch: AIMessage = AIMessage(content="")
    last_speaker: str = Field(default="")
    next_speaker: str = Field(default="")
    judge_decision: AIMessage = AIMessage(content="")
    replices_counter: int = 0
