from bedrock_agentcore.runtime import BedrockAgentCoreApp
from core.graph_engine import build_graph
from langchain_core.messages import HumanMessage

app = BedrockAgentCoreApp()
graph = build_graph() # Memory management handled below

@app.entrypoint
async def handle_request(payload):
    # AgentCore automatically provides session context
    user_input = payload.get("prompt")
    session_id = payload.get("session_id") # Provided by the Bedrock Runtime
    
    # Pass session_id to LangGraph's config for state persistence
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "config": {
            "goal": "Process retail banking inquiry", # You can make this dynamic
            "tools": ["check_balance", "validate_customer"]
        }
    }
    # Invoke your existing agent logic
    result = await graph.ainvoke(
        initial_state, 
        config=config
    )
    print("Final response:", result)
    # return result.get("response", "I'm sorry, I couldn't process that.")
    return {"response": result.get("response")}

if __name__ == "__main__":
    app.run() # Starts the AgentCore-compatible server