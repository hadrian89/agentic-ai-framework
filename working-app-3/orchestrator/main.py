# orchestrator/main.py
import uuid
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import pathlib

app = FastAPI(title="Agentic Orchestrator (starter)")

# Simple in-memory session store (for demo only)
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Load policy
POLICY_FILE = pathlib.Path(__file__).resolve().parents[1] / "policy" / "policies.json"
with open(POLICY_FILE) as f:
    POLICIES = json.load(f)

# Agent definitions (simplified)
AGENT_DEFS = {
    "payments-agent": {
        "id": "payments-agent",
        "prompt_template": (pathlib.Path(__file__).resolve().parents[0] / "prompt_templates" / "payments_prompt.txt").read_text(),
        "tools": ["create_payment"]
    }
}

# Tool registry: mapping tool name --> URL for demo
TOOL_URLS = {
    "create_payment": "http://127.0.0.1:8001/create_payment"
}

class StartSessionRequest(BaseModel):
    agent_id: str

class MessageRequest(BaseModel):
    text: str

@app.post("/sessions", status_code=201)
def start_session(body: StartSessionRequest):
    if body.agent_id not in AGENT_DEFS:
        raise HTTPException(status_code=404, detail="Agent not found")
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "agent_id": body.agent_id,
        "messages": []
    }
    return {"session_id": session_id, "agent_id": body.agent_id}

@app.post("/sessions/{session_id}/message")
def post_message(session_id: str, msg: MessageRequest):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = SESSIONS[session_id]
    text = msg.text
    session["messages"].append({"role": "user", "text": text})

    # build prompt (very simple)
    agent = AGENT_DEFS[session["agent_id"]]
    prompt = agent["prompt_template"].replace("{{user_input}}", text)

    # call mock LLM to decide action
    decision = mock_llm_decide(prompt, text)

    # Decision has either type 'final' or 'tool'
    if decision["type"] == "final":
        ai_text = decision["text"]
        session["messages"].append({"role": "assistant", "text": ai_text})
        return {"type": "final", "response": ai_text}
    elif decision["type"] == "tool":
        tool_name = decision["tool"]
        tool_input = decision["tool_input"]

        # policy enforcement example
        if tool_name == "create_payment":
            ok, msg = enforce_payment_policy(tool_input)
            if not ok:
                return {"type": "error", "reason": msg}

        # call the tool (HTTP)
        tool_url = TOOL_URLS.get(tool_name)
        if not tool_url:
            raise HTTPException(status_code=500, detail="Tool not registered")

        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.post(tool_url, json=tool_input)
                r.raise_for_status()
                tool_result = r.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Tool call failed: {e}")

        # append tool result to session and ask LLM to finalize
        session["messages"].append({"role": "tool", "tool": tool_name, "result": tool_result})

        # For demo: after tool call, mock LLM returns a final answer summarizing result
        final_text = f"Payment result: {tool_result.get('status')}. Payment ID: {tool_result.get('payment_id')}"
        session["messages"].append({"role": "assistant", "text": final_text})
        return {"type": "final", "response": final_text, "tool_result": tool_result}
    else:
        raise HTTPException(status_code=500, detail="Unknown decision type")

def mock_llm_decide(prompt: str, user_text: str) -> Dict[str, Any]:
    """
    Very simple heuristic mock LLM:
    - if text contains the word 'pay' or 'payment' -> call create_payment tool
    - otherwise respond with a simple assistant reply
    """
    lowercase = user_text.lower()
    if "pay " in lowercase or "payment" in lowercase or "transfer" in lowercase:
        # Attempt to parse amount and account in a naive way (demo only)
        # Very simple parsing: find first number as amount, find 8-digit account number and a sort code with pattern dd-dd-dd
        import re
        amount_match = re.search(r"(\d+(?:\.\d+)?)", user_text)
        account_match = re.search(r"(\b\d{8}\b)", user_text)
        sort_code_match = re.search(r"(\b\d{2}-\d{2}-\d{2}\b)", user_text)

        amount = float(amount_match.group(1)) if amount_match else 0.0
        recipient_account = account_match.group(1) if account_match else ""
        sort_code = sort_code_match.group(1) if sort_code_match else ""

        tool_input = {
            "amount": amount,
            "currency": "GBP",
            "recipient": {
                "name": "Unknown Recipient",
                "account_number": recipient_account,
                "sort_code": sort_code
            },
            "idempotency_key": str(uuid.uuid4())
        }
        return {"type": "tool", "tool": "create_payment", "tool_input": tool_input}
    else:
        return {"type": "final", "text": "I can help with that. For payments say: please pay 100 GBP to [name] account 12345678 sort 12-34-56."}

def enforce_payment_policy(tool_input: Dict[str, Any]) -> (bool, str):
    """
    Example policy enforcement based on policy/policies.json
    """
    max_without_2fa = POLICIES.get("payments", {}).get("max_without_2fa", 100.0)
    amount = tool_input.get("amount", 0.0)
    if amount > max_without_2fa:
        return False, f"Payments above {max_without_2fa} GBP require 2FA (policy)."
    return True, "ok"

@app.get("/openapi.yaml")
def openapi_spec():
    # serve the simple OpenAPI file
    openapi_path = pathlib.Path(__file__).resolve().parents[0] / "openapi.yaml"
    return openapi_path.read_text()
