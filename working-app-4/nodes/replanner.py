from core.state import AgentState

def replanner_node(state: AgentState) -> AgentState:
    classification = state.get("last_classification")

    # User asked a clarification about same goal
    if classification == "CLARIFICATION":
        return {
            **state,
            "digression_detected": False,
            "journey_status": "collecting_info"
        }

    # True digression → reset journey within same agent
    if classification == "DIGRESSION":
        return {
            **state,
            "plan": [],
            "collected_slots": {},
            "missing_slots": state["required_slots"].copy(),
            "journey_status": "planning",
            "digression_detected": False
        }

    return state
