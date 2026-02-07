from tools.registry import get_tool

def executor_node(state):

    user_input = state["input"].lower()
    tools = state["config"]["tools"]

    results = []

    # very simple intent-to-tool mapping
    if "balance" in user_input and "check_balance" in tools:
        tool = get_tool("check_balance")

        if tool:
            results.append(tool({"account": "12345678"}))
        else:
            results.append({"error": "Tool not found: check_balance"})


    elif "customer" in user_input and "validate_customer" in tools:
        tool = get_tool("validate_customer")
        results.append(tool({"customer_id": "CUST001"}))

    state["tool_results"] = results
    return state
