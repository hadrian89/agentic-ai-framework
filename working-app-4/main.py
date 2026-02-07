from core.graph import build_agent_graph

agent = build_agent_graph()

initial_state = {
    # 👇 REQUIRED INPUTS (NOT part of AgentState)
    "agent_name": "payment_agent.yaml",   # or "payment_agent.yaml"
    "goal_id": "make_payment",

    # 👇 first user message
    "last_user_message": "Send £50 to John"
}
print("INITIAL STATE:", initial_state)
result = agent.invoke(initial_state)

print("\nFINAL RESULT:\n", result)
