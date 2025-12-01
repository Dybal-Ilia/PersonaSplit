from langgraph.graph import StateGraph, END, START
from src.utils.logger import logger
from src.core.schemas.state import ChatState
from src.core.agents.agent import Orchestrator, Judge, Persona
from typing import List

class GraphFactory:

    def __init__(self, agents_list: List[str]):
        self.orchestrator = Orchestrator(name="orchestrator")
        self.judge = Judge(name="judge")
        self.agents_list = agents_list


    def build_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("Orchestrator", self.orchestrator.run)
        graph.add_node("Judge", self.judge.run)
        graph.add_edge(START, "Orchestrator")
        for agent_name in self.agents_list:
            agent = Persona(name=agent_name)
            graph.add_node(agent_name, agent.run)
            graph.add_edge(agent_name, "Orchestrator")
        conditional_map = {name: name for name in self.agents_list}
        conditional_map["judge"] = "Judge"
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

        if next_speaker == "judge":
            return "judge"
        
        if next_speaker in debators:
            return next_speaker
        
        return "judge"







        

        
