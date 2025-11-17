from typing import Annotated, List
from langchain_groq.chat_models import ChatGroq
from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from src.utils.logger import logger
from src.utils.loaders import load_yaml
from src.core.schemas.state import ChatState
from abc import abstractmethod, ABC
load_dotenv()

prompts_path = os.getenv("PROMPTS_PATH")
API_KEY = os.getenv("GROQ_API_KEY")




class BaseAgent(ABC):
    def __init__(self, name:str, model:str="llama-3.1-8b-instant"):
        self.name = name.strip().lower()
        self.llm = ChatGroq(model=model,
                            api_key=API_KEY,
                            max_tokens=1024)
        self.prompt = ChatPromptTemplate.from_template(load_yaml(prompts_path)[self.name]["system_prompt"])
        self.chain = self.prompt | self.llm


    @abstractmethod
    async def run(self, state:ChatState):
        raise NotImplementedError

class Persona(BaseAgent):
    
    async def run(self, state:ChatState):
        logger.info(f"{self.name} called to the debates")
        response: AIMessage = await self.chain.ainvoke({
            "topic": state.topic,
            "history": state.history,
            "recent_history": state.recent_history
        })
        logger.info(f"{self.name} generated a response")
        response = AIMessage(f"{self.name} said: {response.content}")
        return {
            "history_patch": response
        }
    
class Orchestrator(BaseAgent):

    async def run(self, state:ChatState):
        logger.info(f"{self.name} called to the debates")
        if state.replices_counter == 10:
            logger.warning(f"Turn limit ({state.replices_counter}) reached. Forcing FINISH.")
            return {"next_speaker": "finish"}
        response: AIMessage = await self.chain.ainvoke({
            "debators": state.debators,
            "history": state.history,
            "recent_history": state.recent_history,
            "last_speaker": state.last_speaker
        })
        logger.info(f"{self.name} generated a response")
        cleaned_response = response.content.strip().lower()
        options = [debator for debator in state.debators if debator != state.last_speaker]
        valid_options = options + ["finish"]
        if cleaned_response not in valid_options:
            return {
                "next_speaker": valid_options[0]
                }
        logger.info(f"Next speaker is: {cleaned_response}")
        return {
            "next_speaker": cleaned_response
        }

class HistoryManager(BaseAgent):

    def __init__(self, name:str, history_size:int, model:str="openai/gpt-oss-120b"):
        super().__init__(name, model)
        self.history_size = history_size

    async def run(self, state: ChatState):
        logger.info(f"{self.name} called to manage history")
        
        new_message = state.history_patch
        if not new_message:
            return {}

        current_window = state.recent_history

        new_window = current_window + [new_message]

        if len(new_window) > self.history_size:
            new_window = new_window[-self.history_size:]
        
        return {
            "history": [new_message], 
            "recent_history": new_window, 
            "history_patch": None,
            "replices_counter": state.replices_counter + 1
        }

class Judge(BaseAgent):

    async def run(self, state:ChatState):
        logger.info(f"{self.name} called to the debates")
        response: AIMessage = await self.chain.ainvoke({
            "history": state.history
        })
        logger.info(f"{self.name} generated a response")
        return {
            "judge_decision": response
        }