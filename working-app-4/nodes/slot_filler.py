from core.state import AgentState

def slot_filler_node(state):
    # First turn — nothing to fill yet
    if not state.get("last_user_message"):
        return state

    user_input = state["last_user_message"].lower()

    # Example slot filling logic (stub)
    if "amount" in user_input:
        state["collected_slots"]["amount"] = "parsed_amount"

    return state

