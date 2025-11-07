from typing import Annotated, List
from pydantic import BaseModel, Field
from langchain_ollama.chat_models import ChatOllama
from  langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
import logging
import yaml
from dotenv import load_dotenv
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

load_dotenv()

prompts_path = os.getenv("PROMPTS_PATH")


class AgentState(BaseModel):
    topic: str = Field(..., description="The topic provided by a user's input")
    messages: Annotated[List[BaseMessage], add_messages] = Field(..., description="The history of the debates")


class Agent:
    def __init__(self, name:str, model:str = 'llama3.1'):
        self.name = name.strip().lower()
        self.llm = ChatOllama(model=model, temperature=0.5)
        self.prompt = self._get_prompt()
        self.history: List[str] = []
        self.graph = self._build_graph()
    
    def _get_prompt(self):
        try:
            with open(prompts_path, "r") as f:
                all_prompts = yaml.safe_load(f)
                persona_prompt = all_prompts[self.name.strip().lower()]["system_prompt"]
                llm_prompt = ChatPromptTemplate.from_template(persona_prompt)
                logger.info(f"System prompt for {self.name} loaded successfully")
        except FileNotFoundError:
            logger.error(f"Prompts file does not exist")
            exit()
        except Exception as e:
            logger.error(f"An error occurred while loading prompt: {str(e)}")
            exit()

        return llm_prompt

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("LLM_CALL", self._llm_call)
        graph.add_node("SUMMARIZER", self._summarize)
        graph.add_edge(START, "LLM_CALL")
        graph.add_edge("LLM_CALL", "SUMMARIZER")
        graph.add_edge("SUMMARIZER", END)
        return graph.compile()
    
    def _llm_call(self, state: AgentState) -> AgentState:
        """This node is responsible for llm calling and generating a response"""
        chain = self.prompt | self.llm
        response = chain.invoke({
            "topic": state.topic,
            "messages": state.messages,
            "history": self.history
        })
        content = response.content.strip()
        self.history.append(content)
        return state

    def _summarize(self, state: AgentState) -> AgentState:
        """This node is responsible for summarizing messages"""
        prompt_template = """ You are an AI assistant resposible for text summarization.
        You are given message to be summarized: {history}. Your goal is to slightly summarize the message, yet keep it informative.
        Try to higlight most important things, but if you decide that something can be potentially important leave it as it is.
        Do not make up anything that did not exist in the original message. You are to reduce the original message a little bit.
        Ommit sayings like 'Here is summarized text:', just give the summarized text.
        Avoid any text formatting, just plain text.
        """
        summarizer_prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = summarizer_prompt | self.llm
        response = chain.invoke({
            "history": self.history[-1]
        })
        summary = response.content.strip()
        state.messages = AIMessage(content=f"{self.name} said: {summary}")
        return state
    
    def run(self, topic: str, messages: Annotated[List[BaseMessage], add_messages]):
        init_state = AgentState(
            topic=topic,
            messages=messages
        )
        result = self.graph.invoke(init_state)
        return result