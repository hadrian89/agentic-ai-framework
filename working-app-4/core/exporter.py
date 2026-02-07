import yaml

def export_execution_to_yaml(state) -> str:
    export_data = {
        "agent": state["agent_name"],
        "goal": state["goal_id"],
        "plan": state["plan"],
        "slots": state["collected_slots"],
        "result": state.get("tool_result"),
        "trace": state.get("trace", []),
    }

    return yaml.dump(export_data, sort_keys=False)
