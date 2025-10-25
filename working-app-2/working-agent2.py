import yaml
from pathlib import Path
from typing import Dict, Any
import ollama  # assuming ollama-py client
import networkx as nx

# -----------------------------
# Load agent definitions
# -----------------------------
def load_agent_yaml(agent_file: str) -> Dict[str, Any]:
    with open(agent_file, "r") as f:
        return yaml.safe_load(f)

def load_all_agents(agent_dir: str) -> Dict[str, Dict[str, Any]]:
    agents = {}
    for file in Path(agent_dir).glob("*.yaml"):
        agent = load_agent_yaml(file)
        agents[agent["id"]] = agent
    return agents

# -----------------------------
# Define graph nodes
# -----------------------------
class ExecutionNode:
    def __init__(self, agent):
        self.agent = agent

    def run(self, input_data):
        print(f"[ExecutionNode] Running agent {self.agent['name']} with input: {input_data}")
        # Here you would call the agent's LLM via Ollama
        # client = ollama()
        prompt_file = Path(self.agent["prompt_template"]).read_text()
        response = ollama.chat(model=self.agent["llm"], messages=[{"role": "user", "content": prompt_file}])
        return response

class MonitorNode:
    def monitor(self, output):
        print(f"[MonitorNode] Monitoring output: {output}")
        # simple monitor, in real-world: success/failure detection
        return True if output else False

class PlannerNode:
    def plan(self, goal):
        print(f"[PlannerNode] Creating plan for goal: {goal}")
        return {"steps": ["execute_agent", "monitor_result"]}

class ReplannerNode:
    def replan(self, goal, failed_step):
        print(f"[ReplannerNode] Replanning for goal: {goal}, failed_step: {failed_step}")
        return {"steps": ["execute_agent", "monitor_result", "retry_agent"]}

# -----------------------------
# Orchestrator
# -----------------------------
class AgenticOrchestrator:
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.graph = nx.DiGraph()

    def build_graph(self):
        # Nodes: planner -> execution -> monitor -> (replanner)
        for agent_id, agent in self.agents.items():
            self.graph.add_node(f"{agent_id}_planner", obj=PlannerNode())
            self.graph.add_node(f"{agent_id}_execution", obj=ExecutionNode(agent))
            self.graph.add_node(f"{agent_id}_monitor", obj=MonitorNode())
            self.graph.add_node(f"{agent_id}_replanner", obj=ReplannerNode())

            # Connect nodes
            self.graph.add_edge(f"{agent_id}_planner", f"{agent_id}_execution")
            self.graph.add_edge(f"{agent_id}_execution", f"{agent_id}_monitor")
            self.graph.add_edge(f"{agent_id}_monitor", f"{agent_id}_replanner")

    def run_agent(self, agent_id, goal):
        planner: PlannerNode = self.graph.nodes[f"{agent_id}_planner"]["obj"]
        execution: ExecutionNode = self.graph.nodes[f"{agent_id}_execution"]["obj"]
        monitor: MonitorNode = self.graph.nodes[f"{agent_id}_monitor"]["obj"]
        replanner: ReplannerNode = self.graph.nodes[f"{agent_id}_replanner"]["obj"]

        plan = planner.plan(goal)
        for step in plan["steps"]:
            if step == "execute_agent":
                output = execution.run(goal)
            elif step == "monitor_result":
                success = monitor.monitor(output)
                if not success:
                    replanned = replanner.replan(goal, "execution_failed")
                    print(f"[Orchestrator] Replanned steps: {replanned}")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    agents = load_all_agents("./agents")
    orchestrator = AgenticOrchestrator(agents)
    orchestrator.build_graph()

    # Run multiple agents
    goals = {
        "payments-agent": "Make payment to John Doe 500 USD",
        "statement-agent": "Get last 3 months statement"
    }
    for agent_id, goal in goals.items():
        orchestrator.run_agent(agent_id, goal)


# Observations

# Agents are executing and monitored correctly
# Each ExecutionNode produced an output, and the MonitorNode logged it.

# Ollama LLMs are responding
# The responses from phi4-mini are complete and structured (text and JSON).

# Framework behaves as expected
# The flow Planner → Execution → Monitor works for multiple agents simultaneously.