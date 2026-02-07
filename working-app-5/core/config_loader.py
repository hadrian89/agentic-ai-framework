import yaml

def load_agent_config(agent_id):
    path = f"agents/{agent_id}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)

