from core.state import AgentState

def execute_payment(state: AgentState) -> dict:
    # Simulated AEM call
    return {
        "status": "SUCCESS",
        "transaction_id": "TXN123456",
        "amount": state["collected_slots"]["amount"],
    }
