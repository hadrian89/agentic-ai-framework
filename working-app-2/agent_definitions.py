import yaml
from pathlib import Path

class AgentDefinition:
    def __init__(self, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        self.id = data["id"]
        self.name = data["name"]
        self.version = data.get("version", "0.1.0")
        self.description = data.get("description", "")
        self.llm = data.get("llm", "mock")
        self.prompt_template = Path(path).parent.parent / data.get("prompt_template", "")
        self.tools = data.get("tools", [])
        self.policies = data.get("policies", [])
        self.goals = data.get("goals", [])

def load_agents(agent_dir="agents"):
    agents = []
    for file in Path(agent_dir).glob("*.yaml"):
        agents.append(AgentDefinition(file))
    return agents
