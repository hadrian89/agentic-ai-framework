import yaml
from llm_client import LLMClient
from agent_core import Agent

class AgentManager:
    def __init__(self):
        self.agents = {}
        self.llm_client = LLMClient(model="phi4-mini")

    def load_agents(self, yaml_files):
        for file in yaml_files:
            with open(file, "r") as f:
                config = yaml.safe_load(f)
                agent = Agent(
                    id=config["id"],
                    name=config["name"],
                    description=config["description"],
                    llm_client=self.llm_client,
                    prompt_template=config["prompt_template"],
                    tools=config.get("tools", []),
                    policies=config.get("policies", [])
                )
                self.agents[config["id"]] = agent
                print(f"[AgentManager] Loaded: {config['name']}")
        return self.agents

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)
