# langgraph_runtime.py
from langgraph.graph import StateGraph, START, END
from agent_core import ExecutionNode


class LangGraphRuntime:
    def __init__(self):
        # The state will be a dictionary shared across nodes
        self.graph = StateGraph(dict)

    def build_from_plan(self, plan):
        """
        Dynamically builds a LangGraph execution flow from plan steps.
        Each step is a node that runs its associated tool or action.
        """
        prev_node = None

        for step in plan.get("steps", []):
            node_id = step["id"]
            action_text = step["action"]

            def make_node_fn(action=action_text, node=node_id):
                def node_fn(state):
                    executor = ExecutionNode(action)
                    result = executor.execute()
                    state[node] = result  # merge into shared state
                    return state
                return node_fn

            self.graph.add_node(node_id, make_node_fn())

            if prev_node is None:
                self.graph.add_edge(START, node_id)
            else:
                self.graph.add_edge(prev_node, node_id)

            prev_node = node_id

        if prev_node is not None:
            self.graph.add_edge(prev_node, END)

        # ✅ Return the compiled graph runner (NOT a dict)
        return self.graph.compile()

    
    def run(self, compiled_graph, initial_state=None):
        print("[LangGraphRuntime] Running plan...")

        if not hasattr(compiled_graph, "invoke"):
            raise TypeError(f"Expected a compiled LangGraph, got {type(compiled_graph).__name__}")

        result = compiled_graph.invoke(initial_state or {}, config={"recursion_limit": 100})
        print("[LangGraphRuntime] Execution completed.")
        return result

