from langchain.messages import AIMessage
from langgraph.graph import StateGraph, END, START
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import logger
from src.utils.loaders import load_yaml
from src.core.schemas.state import ChatState
from src.core.agents.agent import Orchestrator, HistoryManager, Judge, Persona
from typing import List

class GraphFactory:

    def __init__(self, agents_list: List[str]):
        self.orchestrator = Orchestrator(name="orchestrator")
        self.history_manager = HistoryManager(name="history_manager", history_size=4)
        self.judge = Judge(name="judge")
        self.agents_list = agents_list


    def build_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("Orchestrator", self.orchestrator.run)
        graph.add_node("HistoryManager", self.history_manager.run)
        graph.add_node("Judge", self.judge.run)
        graph.add_edge(START, "Orchestrator")
        for agent_name in self.agents_list:
            agent = Persona(name=agent_name)
            graph.add_node(agent_name, agent.run)
            graph.add_edge(agent_name, "HistoryManager")
        graph.add_edge("HistoryManager", "Orchestrator")       
        conditional_map = {name: name for name in self.agents_list}
        conditional_map["finish"] = "Judge"
        graph.add_conditional_edges(
            source="Orchestrator",
            path=self.route_debates,
            path_map=conditional_map
        ) 
        graph.add_edge("Judge", END)
        return graph.compile()
    

    @staticmethod
    async def route_debates(state: ChatState):
        next_speaker = state.next_speaker
        debators = state.debators

        if next_speaker == "finish":
            return "finish"
        
        if next_speaker in debators:
            return next_speaker
        
        return "finish"







        

        
