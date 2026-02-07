from core.agent_loader import load_agent_config


def start_node(state):
    agent_name = state.get("agent_name")
    goal_id = state.get("goal_id")

    if not agent_name:
        raise ValueError("agent_name missing in initial_state")

    if not goal_id:
        raise ValueError("goal_id missing in initial_state")

    agent_config = load_agent_config(agent_name)

    if goal_id not in agent_config["goals"]:
        raise ValueError(f"Unknown goal_id: {goal_id}")

    return {
        "agent_config": agent_config,
        "goal_config": agent_config["goals"][goal_id],
        "journey_status": "planning",
    }
