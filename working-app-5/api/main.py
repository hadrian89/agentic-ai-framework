from fastapi import FastAPI
# IMPORTANT: this line registers tools
import tools.banking_tools

from core.graph_engine import build_graph
from core.config_loader import load_agent_config
from core.memory import InMemoryStore

app = FastAPI()

graph = build_graph()

@app.post("/agent/{agent_id}/chat")
def chat(agent_id: str, payload: dict):

    session_id = payload.get("session_id")
    message = payload.get("message")

    config = load_agent_config(agent_id)

    state = {
        "input": message,
        "config": config,
        "history": InMemoryStore.get(session_id)
    }

    result = graph.invoke(state)

    InMemoryStore.update(session_id, message)

    return {
        "reply": result.get("response"),
        "agent": agent_id
    }
