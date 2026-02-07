from llm.provider import get_llm
llm = get_llm()


def responder_node(state):

    prompt = f"""
    You are a UK retail banking assistant.

    USER QUESTION:
    {state['messages']}

    TOOL RESULTS (REAL DATA):
    {state.get('tool_results')}

    RULES:
    - Answer ONLY using the tool results above
    - Do NOT say you cannot access information
    - Do NOT hallucinate
    - Be concise

    Provide a clear answer.
    """

    reply = llm.generate(prompt)

    state["response"] = reply
    return state
