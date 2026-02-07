from core.state import AgentState


def execution_node(state: AgentState):
    if "goal_config" not in state:
        raise RuntimeError("Execution called before planner set goal_config")

    required = state["goal_config"]["required_slots"]
    filled = state.get("slots", {})

    missing = [s for s in required if s not in filled]

    if missing:
        return {
            **state,
            "missing_slots": missing,
            "journey_status": "collecting_info",
        }

    return {
        "missing_slots": missing,
        "journey_status": "ready_for_execution",
    }
