# """
# agent_loader.py
# Loads YAML-defined agents from a directory and instantiates Agent objects.
# """

# import yaml
# from pathlib import Path
# from typing import List, Dict, Any
# from agentic_framework import Planner, ExecutionNode, MonitorNode, Replanner, Agent, DefaultLLM
# from policy_engine import PolicyEngine
# import os

# class AgentLoader:
#     def __init__(self, agents_dir: str = "./agents"):
#         self.agents_dir = Path(agents_dir)

#     def load_agent_config(self, file_path: Path) -> Dict[str, Any]:
#         with open(file_path, "r") as f:
#             return yaml.safe_load(f)

#     def load_all(self) -> List[Agent]:
#         agents = []
#         for yaml_file in sorted(self.agents_dir.glob("*.yaml")):
#             cfg = self.load_agent_config(yaml_file)
#             agents.append(self.create_agent(cfg))
#         return agents

#     def create_agent(self, cfg: Dict[str, Any]) -> Agent:
#         llm_name = cfg.get("llm", "mock")
#         llm = DefaultLLM(llm_name)

#         planner = Planner(llm=llm)
#         replanner = Replanner(llm=llm)

#         # load policies
#         policy_files = []
#         for p in cfg.get("policies", []):
#             # policy may be file path or object - assume path string
#             policy_files.append(os.path.join(os.getcwd(), p) if not Path(p).is_absolute() else p)
#         policy_engine = PolicyEngine(policy_files) if policy_files else None

#         exec_node = ExecutionNode(policy_engine=policy_engine)
#         monitor = MonitorNode()

#         # register tenant-specific tools if mentioned in YAML (names must map to actual functions)
#         # For extensibility, you can import and register real tools here.
#         # ExecutionNode already registers mock_make_payment, mock_get_statement by default.

#         agent = Agent(name=cfg.get("name", cfg.get("id", "agent")), planner=planner, exec_node=exec_node, monitor=monitor, replanner=replanner, meta=cfg)
#         return agent
