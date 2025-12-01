from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from src.utils.logger import logger
from src.utils.loaders import load_yaml
from src.core.schemas.state import ChatState
from src.core.memory_client import memory_client
from abc import abstractmethod, ABC
from httpx import HTTPStatusError
import asyncio
load_dotenv()

prompts_path = os.getenv("PROMPTS_PATH")
API_KEY = os.getenv("GROQ_API_KEY")




class BaseAgent(ABC):
    def __init__(self, name:str, model:str="openai/gpt-oss-20b", max_tokens:int=300):
        self.name = name.strip().lower()
        self.memory = memory_client
        self.llm = ChatGroq(model=model,
                            api_key=API_KEY,
                            max_tokens=max_tokens)
        self.prompt = ChatPromptTemplate.from_template(load_yaml(prompts_path)[self.name]["system_prompt"])
        self.chain = self.prompt | self.llm


    @abstractmethod
    async def run(self, state:ChatState):
        raise NotImplementedError

class Persona(BaseAgent):
    
    async def run(self, state:ChatState):
        logger.info(f"{self.name} called to the debates")
        try:
            memories = self.memory.search(
                query=state.topic, 
                user_id=state.session_id,
                limit=5
            )
            context = "\\n".join(memories) or state.history_patch.content
        except Exception as e:
            logger.warning(f"Memory search failed: {e}")
            context = "No history yet."
        logger.info(f"Context for {self.name}:\n{context}")
        response: AIMessage = await self.chain.ainvoke({
            "topic": state.topic,
            "context": context
        })
        logger.info(f"{self.name} generated a response")
        await asyncio.get_event_loop().run_in_executor(
            None,
            memory_client.add,
            {"messages":[{"role":"user","content":f"{self.name} says: {response.content}"}],
             "user_id":state.session_id})
        response = AIMessage(f"{self.name} said: {response.content}")
        return {
            "history_patch": response,
            "last_speaker": self.name,
            "replices_counter": state.replices_counter + 1
        }
    
class Orchestrator(BaseAgent):

    async def run(self, state:ChatState):
        logger.info(f"{self.name} called to the debates")
        if state.replices_counter == 10:
            logger.warning(f"Turn limit ({state.replices_counter}) reached. Forcing FINISH.")
            return {"next_speaker": "judge"}
        try:
            memories = self.memory.search(
                query=state.topic, 
                user_id=state.session_id,
                limit=5
            )
            context = "\\n".join(memories) or state.history_patch.content
        except Exception as e:
            logger.warning(f"Memory search failed: {e}")
            context = "No history yet."
        logger.info(f"Context for {self.name}:\n{context}")
        response: AIMessage = await self.chain.ainvoke({
            "debators": state.debators,
            "context": context,
            "last_speaker": state.last_speaker
        })
        logger.info(f"{self.name} generated a response")
        cleaned_response = response.content.strip().lower()
        options = [debator for debator in state.debators if debator != state.last_speaker]
        valid_options = options + ["judge"]
        if cleaned_response not in valid_options:
            return {
                "next_speaker": valid_options[0]
                }
        logger.info(f"Next speaker is: {cleaned_response}")
        return {
            "next_speaker": cleaned_response
        }


class Judge(BaseAgent):

    def __init__(self, name:str, model:str="openai/gpt-oss-20b", max_tokens:int=500):
        super().__init__(name, model, max_tokens)

    async def run(self, state:ChatState):
        logger.info(f"{self.name} called to the debates")
        try:
            memories = self.memory.search(
                query=state.topic, 
                user_id=state.session_id,
                limit=20
            )
            context = "\\n".join(memories) or state.history_patch.content
        except Exception as e:
            logger.warning(f"Memory search failed: {e}")
            context = "No history yet."
        logger.info(f"Context for {self.name}:\n{context}")
        response: AIMessage = await self.chain.ainvoke({
            "context": context
        })
        logger.info(f"{self.name} generated a response")
        return {
            "judge_decision": response
        }