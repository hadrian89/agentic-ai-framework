import yaml
from pathlib import Path

class AgentConfigError(Exception):
    pass


def load_agent_config(agent_name: str) -> dict:
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "agents" / f"{agent_name}_agent.yaml"

    print("DEBUG loading agent config from:", config_path)

    if not config_path.exists():
        raise AgentConfigError(f"Agent config not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    validate_agent_config(config)
    return config


def validate_agent_config(config: dict):
    required_keys = ["agent", "goals", "policies", "prompts"]

    for key in required_keys:
        if key not in config:
            raise AgentConfigError(f"Missing required key: {key}")

    if not config.get("goals"):
        raise AgentConfigError("At least one goal must be defined")
