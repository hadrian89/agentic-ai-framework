from abc import ABC, abstractmethod
import ollama

# Optional: fallback friendly questions
FIELD_QUESTIONS = {
    "amount": "How much would you like to transfer?",
    "payee_location": "Where is the payee located?",
    "payee_type": "Is the payee new or existing?",
    "channel": "Which channel would you like to use (mobile app / online banking)?",
    "account_number": "What is your account number?",
    "date_range": "Which date range do you want the statement for?",
}

class Node(ABC):
    @abstractmethod
    def run(self, context):
        pass

# -------------------------
# User input node
# -------------------------
class UserInputNode(Node):
    def __init__(self, use_ollama=False, model="llama2"):
        self.use_ollama = use_ollama
        self.model = model
        if use_ollama:
            self.client = ollama

    def run(self, context):
        goal = context.get("goal", "")
        fields = [part.split()[0].strip() for part in goal.split("AND")]

        if "context_values" not in context:
            context["context_values"] = {}

        for field in fields:
            if field not in context["context_values"]:
                if self.use_ollama:
                    prompt = f"Ask the user a natural language question to get the value for '{field}' in the context of banking."
                    response = self.client.generate(model=self.model, prompt=prompt)
                    question = response.get("text", FIELD_QUESTIONS.get(field, f"Please provide '{field}'"))
                else:
                    question = FIELD_QUESTIONS.get(field, f"Please provide '{field}'")
                value = input(f"{question} ")
                context["context_values"][field] = value

        print(f"[UserInputNode] Collected values: {context['context_values']}")
        return context

# -------------------------
# Planner node
# -------------------------
class PlannerNode(Node):
    def run(self, context):
        print(f"[PlannerNode] Planning for goal: {context.get('goal')}")
        agent_tools = context.get("agent_tools", [])
        context_values = context.get("context_values", {})

        # Simple goal evaluation: check all fields are filled
        missing = False
        for part in context.get("goal", "").split("AND"):
            field = part.split()[0].strip()
            if field not in context_values or context_values[field] == "":
                missing = True

        if missing:
            print("[PlannerNode] Missing values detected, user input required.")
            context["plan"] = "wait_for_input"
        else:
            context["plan"] = agent_tools[0] if agent_tools else "no-tool-found"

        return context

# -------------------------
# Execution node
# -------------------------
class ExecutionNode(Node):
    def run(self, context):
        print(f"[ExecutionNode] Executing plan: {context.get('plan')}")
        # Mock execution: in real system, call tool or LLM here
        context["result"] = f"Executed {context.get('plan')} with data {context.get('context_values')}"
        return context

# -------------------------
# Monitor node
# -------------------------
class MonitorNode(Node):
    def run(self, context):
        print(f"[MonitorNode] Monitoring result: {context.get('result')}")
        # Basic success/failure detection
        context["status"] = "success" if "Executed" in context.get("result") else "failed"
        return context

# -------------------------
# Replanner node
# -------------------------
class ReplannerNode(Node):
    def run(self, context):
        if context.get("status") == "failed":
            print(f"[ReplannerNode] Replanning for goal: {context.get('goal')}")
            context["plan"] = context.get("agent_tools", ["no-tool-found"])[0] + "_retry"
        return context
