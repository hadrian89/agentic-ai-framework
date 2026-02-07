from core.state import AgentState
from policies.registry import POLICY_REGISTRY

class PolicyViolation(Exception):
    def __init__(self, policy_name: str):
        super().__init__(f"Policy violation: {policy_name}")
        self.policy_name = policy_name


def policy_executor_node(state: AgentState) -> AgentState:
    policies = state["agent_config"].get("policies", [])

    for policy_name in policies:
        policy_fn = POLICY_REGISTRY.get(policy_name)

        if not policy_fn:
            raise ValueError(f"Unknown policy: {policy_name}")

        passed = policy_fn(state)

        if not passed:
            raise PolicyViolation(policy_name)

    return state
