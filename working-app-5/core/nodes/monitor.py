def monitor_node(state):

    if not state.get("tool_results"):
        state["status"] = "NO_DATA"
    else:
        state["status"] = "OK"

    return state
