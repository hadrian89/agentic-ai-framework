from langgraph.graph import StateGraph
from core.nodes.planner import planner_node
from core.nodes.executor import executor_node
from core.nodes.monitor import monitor_node
from core.nodes.responder import responder_node

from typing import TypedDict

class AgentState(TypedDict):
    input: str
    config: dict
    history: list
    plan: str
    tool_results: list
    response: str

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("monitor", monitor_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "monitor")
    graph.add_edge("monitor", "responder")

    return graph.compile()
