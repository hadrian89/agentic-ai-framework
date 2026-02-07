from llm.ollama_client import OllamaLLM

llm = OllamaLLM()

def planner_node(state):
    prompt = f"""
    User Query: {state['input']}
    Goal: {state['config']['goal']}
    Create simple plan.
    """

    plan = llm.generate(prompt)

    return {"plan": plan}
