import uuid
import re


class Planner:
    def __init__(self, llm_client, prompt_template_path: str):
        self.llm_client = llm_client
        self.prompt_template_path = prompt_template_path

    def read_prompt_template(self) -> str:
        """Read and return the prompt template"""
        try:
            with open(self.prompt_template_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "No valid prompt template found."

    def _sanitize_step(self, step: str) -> str:
        """Make step safe for use as node ID (LangGraph restriction)"""
        safe = re.sub(r"[^a-zA-Z0-9_]+", "_", step.strip())
        return safe[:50]  # limit node ID length

    def plan(self, goal: str):
        """Generate plan steps using LLM"""
        prompt_template = self.read_prompt_template()
        prompt = prompt_template.replace("{goal}", goal)
        response = self.llm_client.generate(prompt)

        # Split into lines, clean up formatting, and sanitize
        raw_steps = [s.strip("-• ") for s in response.splitlines() if s.strip()]
        # raw_steps = [s.strip("-• ") for s in response.splitlines() if s.strip()]
        # steps = [
        #     {"id": f"step_{i}", "action": s}
        #     for i, s in enumerate(raw_steps)
        #     if not s.startswith("###") and len(s.split()) > 3
        # ][:10]  # limit to first 10 useful steps

        steps = []
        for s in raw_steps:
            steps.append({
                "id": self._sanitize_step(s),
                "action": s
            })

        print(f"[Planner] Plan generated with {len(steps)} steps.")
        return {"plan_id": str(uuid.uuid4()), "steps": steps}


class ExecutionNode:
    def __init__(self, step):
        self.step = step

    def execute(self):
        print(f"[ExecutionNode] Executing: {self.step}")
        return f"✅ Completed: {self.step}"


class MonitorNode:
    def __init__(self):
        self.logs = []

    def log(self, message):
        print(f"[MonitorNode] {message}")
        self.logs.append(message)


class Replanner:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def replan(self, failed_step):
        print(f"[Replanner] Replanning after failure: {failed_step}")
        return self.llm_client.generate(f"Replan for failed step: {failed_step}")


class Agent:
    def __init__(self, id, name, description, llm_client, prompt_template, tools, policies):
        self.id = id
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.planner = Planner(llm_client, prompt_template)
        self.tools = tools
        self.policies = policies
        self.monitor = MonitorNode()
        self.replanner = Replanner(llm_client)

    def execute_goal(self, goal):
        print(f"\n[Agent {self.name}] Starting goal: {goal}")
        plan = self.planner.plan(goal)
        results = []

        for step in plan["steps"]:
            executor = ExecutionNode(step["action"])
            try:
                result = executor.execute()
                results.append(result)
                self.monitor.log(result)
            except Exception as e:
                self.monitor.log(f"Failed: {step['action']}")
                replanned = self.replanner.replan(step["action"])
                results.append(replanned)

        print(f"[Agent {self.name}] Execution completed.\n")
        return {"plan": plan, "results": results}
