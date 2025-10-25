from agent_definitions import load_agents
from agent_runner import UserInputNode, PlannerNode, ExecutionNode, MonitorNode, ReplannerNode

# -------------------------
# Load agents
# -------------------------
agents = load_agents()  # Load all YAML agent definitions

# -------------------------
# Initialize nodes
# -------------------------
user_input = UserInputNode(use_ollama=False)  # Set True if you want Ollama generated prompts
planner = PlannerNode()
executor = ExecutionNode()
monitor = MonitorNode()
replanner = ReplannerNode()

# -------------------------
# Run all agents
# -------------------------
for agent in agents:
    print(f"\n--- Running Agent: {agent.id} ---\n")
    for goal_def in agent.goals:
        context = {
            "agent_id": agent.id,
            "goal": goal_def["goal"],
            "agent_tools": agent.tools
        }

        # 1️⃣ Ask for missing user input
        context = user_input.run(context)

        # 2️⃣ Plan execution
        context = planner.run(context)

        # 3️⃣ Execute if plan ready
        if context["plan"] != "wait_for_input":
            context = executor.run(context)
            context = monitor.run(context)
            context = replanner.run(context)

        print(f"\nFinal context for agent {agent.id}: {context}\n")


