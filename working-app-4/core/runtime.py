def handle_user_message(agent, state, user_message: str):
    state["last_user_message"] = user_message
    state["messages"].append({
        "role": "user",
        "content": user_message
    })

    # Slot filling
    state = agent.invoke(state, start_at="slot_filler")

    return state
