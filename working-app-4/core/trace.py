def append_trace(state, event: str, data: dict = None):
    trace = state.get("trace", [])
    trace.append({
        "event": event,
        "data": data or {}
    })
    state["trace"] = trace
    return state
