# tests/test_make_payment_flow.py
import multiprocessing
import time
import requests
from fastapi.testclient import TestClient
import uvicorn
import os
import subprocess
import sys
import threading

# Start the two apps programmatically using subprocesses is complex in tests.
# Instead we import the apps and use TestClient for both.

def test_payment_flow():
    # Import apps
    from orchestrator.main import app as orchestrator_app
    from tools.payments_service import app as payments_app

    from fastapi.testclient import TestClient
    pay_client = TestClient(payments_app)
    orch_client = TestClient(orchestrator_app)

    # Sanity health check by trying to directly call tool (using TestClient)
    payment_payload = {
        "amount": 10.0,
        "currency": "GBP",
        "recipient": {
            "name": "John",
            "account_number": "12345678",
            "sort_code": "12-34-56"
        },
        "idempotency_key": "tid-1"
    }
    r = pay_client.post("/create_payment", json=payment_payload)
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    # Now create session in orchestrator
    r = orch_client.post("/sessions", json={"agent_id": "payments-agent"})
    assert r.status_code == 201
    session_id = r.json()["session_id"]

    # Send message to orchestrator - we expect it to call the tool and return a final response
    message = "Please pay 10 GBP to John account 12345678 sort 12-34-56"
    r = orch_client.post(f"/sessions/{session_id}/message", json={"text": message})
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "final"
    assert "Payment result" in data["response"] or "Payment result" in data.get("tool_result", {}).get("status", "")

