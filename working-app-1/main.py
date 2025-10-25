from agent_manager import AgentManager
from graph_builder import GraphBuilder
from langgraph_runtime import LangGraphRuntime

if __name__ == "__main__":
    manager = AgentManager()

    agents = manager.load_agents([
        "agents/make-payment-agent.yaml",
        "agents/get-statement-agent.yaml"
    ])

    payment_agent = manager.get_agent("payments-agent")
    result = payment_agent.execute_goal("Make a payment to John for £100")

    # 🔹 Generate JSON Graph
    graph_builder = GraphBuilder()
    graph_json = graph_builder.build_from_plan(result["plan"])
    print("\n[Generated JSON Graph]")
    print(graph_json)

    # 🔹 Execute same plan with LangGraph
    runtime = LangGraphRuntime()
    compiled_graph = runtime.build_from_plan(result["plan"])
    runtime.run(compiled_graph, {"goal": "Make a payment"})
