from core.state import AgentState
from tools.registry import TOOL_REGISTRY

def tool_executor_node(state: AgentState) -> AgentState:
    tool_name = state["goal_config"]["tool"]
    tool_fn = TOOL_REGISTRY.get(tool_name)

    if not tool_fn:
        raise ValueError(f"Tool not registered: {tool_name}")

    result = tool_fn(state)

    return {
        **state,
        "tool_result": result,
        "journey_status": "completed",
    }
