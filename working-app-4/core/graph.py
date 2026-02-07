from langgraph.graph import StateGraph
from core.state import AgentState

from nodes.start import start_node
from nodes.planner import planner_node
from nodes.execution import execution_node
from nodes.slot_filler import slot_filler_node
from nodes.digression_detector import digression_detector_node
from nodes.replanner import replanner_node
from nodes.policy_executor import policy_executor_node
from nodes.tool_executor import tool_executor_node
from nodes.responder import responder_node


def build_agent_graph():
    graph = StateGraph(AgentState)

    # --------------------
    # Register ALL nodes
    # --------------------
    graph.add_node("start", start_node)
    graph.add_node("planner", planner_node)
    graph.add_node("execution", execution_node)
    graph.add_node("slot_filler", slot_filler_node)
    graph.add_node("digression_detector", digression_detector_node)
    graph.add_node("replanner", replanner_node)
    graph.add_node("policy_executor", policy_executor_node)
    graph.add_node("tool_executor", tool_executor_node)
    graph.add_node("responder", responder_node)

    # --------------------
    # Entry
    # --------------------
    graph.set_entry_point("start")

    # --------------------
    # Mandatory ordering
    # --------------------
    graph.add_edge("start", "planner")
    graph.add_edge("planner", "execution")

    # --------------------
    # Execution routing
    # --------------------
    graph.add_conditional_edges(
        "execution",
        lambda s: s["journey_status"],
        {
            "collecting_info": "slot_filler",
            "awaiting_user_input": "__end__",
            "ready_for_execution": "policy_executor",
        },
    )

    # Slot filling loop
    graph.add_edge("slot_filler", "execution")

    # Digression detection
    graph.add_edge("execution", "digression_detector")

    graph.add_conditional_edges(
        "digression_detector",
        lambda s: s.get("digression_detected", False),
        {
            True: "replanner",
            False: "policy_executor",
        },
    )

    graph.add_edge("replanner", "execution")

    # Final execution path
    graph.add_edge("policy_executor", "tool_executor")
    graph.add_edge("tool_executor", "responder")
    graph.add_edge("responder", "__end__")

    return graph.compile()
