from pydantic import BaseModel, Field
from typing import Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(BaseModel):
    topic: str = Field(..., description="The topic provided by a user's input")
    messages: Annotated[List[BaseMessage], add_messages] = Field(..., description="The history of the debates")


