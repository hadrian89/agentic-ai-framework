from llm.provider import get_llm
llm = get_llm()


def planner_node(state):
    prompt = f"""
    User Query: {state['input']}
    Goal: {state['config']['goal']}
    Create simple plan.
    """

    plan = llm.generate(prompt)

    return {"plan": plan}
