"""
agentic_framework.py
A demo multi-agent agentic AI framework:
- Planner (LLM via Ollama)
- ExecutionNode (invokes tools / APIs)
- MonitorNode (observes execution)
- Replanner (LLM-driven)
- Orchestrator (ties agents together)

This demo uses the Ollama Python client for LLM calls.
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import re

# Ollama client import — ensure you installed `ollama` or `ollama-python`.
# If your client package is different, change the import accordingly.
import ollama


# -------------------------
# Utilities / Mocked Tools
# -------------------------
# In a production system, these are replaced with real bank APIs (wrapped with security, audit, etc.)

async def mock_make_payment(from_account: str, to_account: str, amount: float, currency: str = "GBP") -> Dict[str, Any]:
    """Mock payment tool — replace with real payment gateway client."""
    await asyncio.sleep(0.4)  # simulate network
    # For demo: fail if amount > 1000 to trigger replanning
    if amount > 1000:
        return {"status": "failed", "reason": "amount_exceeds_authorization_limit"}
    return {"status": "success", "transaction_id": "TXN-" + str(int(amount * 1000))}

async def mock_get_statement(account_id: str, months: int = 1) -> Dict[str, Any]:
    await asyncio.sleep(0.2)
    # return a tiny fake statement object
    return {
        "status": "success",
        "account_id": account_id,
        "period_months": months,
        "transactions": [
            {"id": "1", "amount": -12.50, "desc": "Coffee"},
            {"id": "2", "amount": -120.00, "desc": "Grocery"},
        ]
    }

def extract_json(raw_text: str) -> dict:
    """Extract first JSON object from LLM output."""
    # Match anything that starts with { and ends with } (non-greedy)
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            # fallback empty plan
            return {"goal": "", "steps": []}
    else:
        return {"goal": "", "steps": []}
# -------------------------
# Core Node & Agent Types
# -------------------------

@dataclass
class Step:
    id: str
    action: str         # e.g., "make_payment", "get_statement"
    params: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None

@dataclass
class Plan:
    goal: str
    steps: List[Step] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionNode:
    """Executes steps by calling registered tool functions."""
    def __init__(self):
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.register_tool("make_payment", mock_make_payment)
        self.register_tool("get_statement", mock_get_statement)

    def register_tool(self, name: str, fn: Callable[..., Any]):
        self.tools[name] = fn

    async def execute_step(self, step: Step) -> Step:
        step.status = "running"
        tool = self.tools.get(step.action)
        if not tool:
            step.status = "failed"
            step.result = {"status": "failed", "reason": f"unknown_tool:{step.action}"}
            return step
        try:
            res = await tool(**step.params) if asyncio.iscoroutinefunction(tool) else tool(**step.params)
            step.result = res
            step.status = "success" if res.get("status") == "success" else "failed"
        except Exception as e:
            step.status = "failed"
            step.result = {"status": "failed", "reason": str(e)}
        return step


class MonitorNode:
    """Watches steps and emits events/metrics. Could push to observability pipeline."""
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    async def observe(self, step: Step):
        rec = {"id": step.id, "action": step.action, "status": step.status, "result": step.result}
        self.history.append(rec)
        # Simple print logger — replace with structured logs/metrics exporter
        print(f"[Monitor] observed step={step.id} action={step.action} status={step.status}")

import json
import ast
import re

class Planner:
    """Uses LLM to create a Plan from a goal."""
    def __init__(self, model: str = "llama2", ollama_client=None):
        self.model = model
        self.client = ollama_client  # can be None for now, replace with your LLM client

    async def create_plan(self, goal: str, context: dict = None):
        ctx = context or {}
        prompt = f"""
You are an agentic planner. Create a minimal step-by-step plan (as strict JSON) to achieve the goal.
Goal: {goal}
Context: {json.dumps(ctx)}
Return ONLY JSON with top-level object containing "goal" and "steps" 
(each step has id, action, params).
"""
        # Call your LLM; for demo, you can mock this:
        if self.client:
            response = self.client.generate(self.model, prompt)
            raw = response.text if hasattr(response, "text") else str(response)
        else:
            # Mock response for testing
            raw = '{"goal": "' + goal + '", "steps": [{"id": "step-1", "action": "noop", "params": {}}]}'

        print(f"[Planner] raw model output:\n{raw}")

        # --- parse JSON robustly ---
        payload = None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            # try regex extract {...}
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    payload = json.loads(m.group(0))
                except json.JSONDecodeError:
                    try:
                        # fallback: parse as Python dict
                        payload = ast.literal_eval(m.group(0))
                    except Exception:
                        payload = None
            if payload is None:
                # final fallback: create default plan
                payload = {"goal": goal, "steps": [{"id": "step-1", "action": "noop", "params": {}}]}

        # --- convert to Step objects ---
        steps_raw = payload.get("steps")
        if not steps_raw:
            # if steps are empty, add a noop to prevent infinite replanning
            steps_raw = [{"id": "step-1", "action": "noop", "params": {}}]

        steps = []
        for s in steps_raw:
            steps.append(Step(
                id=str(s.get("id", "step-1")),
                action=s.get("action", "noop"),
                params=s.get("params", {})
            ))

        return Plan(goal=payload.get("goal", goal), steps=steps, metadata={"llm_raw": raw})



class Replanner:
    """When execution fails, ask LLM to adjust the plan."""
    def __init__(self, model: str = "llama3", ollama_client=None):
        self.model = model
        # ensure client exists
        self.client = ollama_client or ollama


    async def replan(self, failed_step: Step, current_plan: Plan, context: Dict[str, Any] = None) -> Plan:
        ctx = context or {}
        prompt = f"""
    You are a replanner. One step failed. Goal: {current_plan.goal}
    Failed step: {json.dumps({'id': failed_step.id, 'action': failed_step.action, 'params': failed_step.params, 'result': failed_step.result})}
    Current plan steps: {json.dumps([{'id':s.id,'action':s.action,'params':s.params,'status':s.status} for s in current_plan.steps])}
    Suggest a revised plan (JSON) to complete the goal. Return JSON with "goal" and "steps".
    """
        response = self.client.generate(self.model, prompt)
        raw = response.text if hasattr(response, "text") else str(response)

        # Try strict JSON first
        try:
            # payload = json.loads(raw)
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = extract_json(raw)
        except Exception:
            # fallback: extract JSON substring
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    payload = json.loads(m.group(0))
                except Exception:
                    # still fails → return empty plan
                    payload = {"goal": current_plan.goal, "steps": []}
            else:
                payload = {"goal": current_plan.goal, "steps": []}

        steps = [
            Step(id=s.get("id", f"step{idx}"), action=s.get("action", "noop"), params=s.get("params", {}))
            for idx, s in enumerate(payload.get("steps", []))
        ]
        return Plan(goal=payload.get("goal", current_plan.goal), steps=steps, metadata={"llm_raw": raw})

# -------------------------
# Agents (task-specialized)
# -------------------------
class Agent:
    def __init__(self, name: str, planner: Planner, exec_node: ExecutionNode, monitor: MonitorNode, replanner: Replanner):
        self.name = name
        self.planner = planner
        self.exec_node = exec_node
        self.monitor = monitor
        self.replanner = replanner

    async def run_goal(self, goal: str, context: Dict[str, Any] = None, depth=0, max_replans=3) -> Plan:
        # 1. Make plan
        print(f"[{self.name}] creating plan for goal: {goal}")
        if depth > max_replans:
            print(f"[{self.name}] max replans reached for goal: {goal}")
            return Plan(goal=goal, steps=[])
        
        plan = await self.planner.create_plan(goal, context or {})
        # 2. Execute steps sequentially, monitor, and call replanner if failure occurs
        for step in plan.steps:
            step = await self.exec_node.execute_step(step)
            await self.monitor.observe(step)

            if step.status != "success":
                print(f"[{self.name}] step {step.id} failed. Asking replanner...")
                plan = await self.replanner.replan(step, plan, context or {})
                return await self.run_goal(plan.goal, context, depth + 1)
        # for idx, step in enumerate(plan.steps):
        #     print(f"[{self.name}] executing step {step.id} -> {step.action}")
        #     step = await self.exec_node.execute_step(step)
        #     await self.monitor.observe(step)

        #     if step.status != "success":
        #         # ask replanner for a new plan
        #         print(f"[{self.name}] step {step.id} failed. Asking replanner...")
        #         plan = await self.replanner.replan(step, plan, context or {})
        #         # restart execution from the top of new plan
        #         print(f"[{self.name}] replaced plan with {len(plan.steps)} steps from replanner")
        #         # simple strategy: re-run newly created plan from start
        #         return await self.run_goal(plan.goal, context)
        # print(f"[{self.name}] plan completed successfully")
        return plan


# -------------------------
# Orchestrator - multi-agent management
# -------------------------
class Orchestrator:
    def __init__(self, ollama_model: str = "phi4-mini"):
        # no self.ollama_client
        self.planner = Planner(model=ollama_model)
        self.replanner = Replanner(model=ollama_model)
        self.exec_node = ExecutionNode()
        self.monitor = MonitorNode()
        # instantiate agents for retail banking tasks
        self.payment_agent = Agent("PaymentAgent", self.planner, self.exec_node, self.monitor, self.replanner)
        self.statement_agent = Agent("StatementAgent", self.planner, self.exec_node, self.monitor, self.replanner)

    async def run(self):
        # Example: run two goals concurrently (simulate multi-agent)
        g1 = "Make a payment of 1500 GBP from account A-123 to new payee B-987 for invoice INV-555"
        g2 = "Get the last month's statement for account A-123 and summarize categories"

        results = await asyncio.gather(
            self.payment_agent.run_goal(g1, context={"user_id": "user-1", "auth_level": "high"}),
            self.statement_agent.run_goal(g2, context={"user_id": "user-1"}),
        )
        return results


# -------------------------
# Driver
# -------------------------
async def main():
    orchestrator = Orchestrator(ollama_model="phi4-mini")
    plans = await orchestrator.run()
    for plan in plans:
        print("FINAL PLAN:", plan.goal)
        if isinstance(plan.goal, dict):
            goal = plan.goal.get("description", str(plan.goal))
        else:
            goal = plan.goal
        for s in plan.steps:
            print(f"  - {s.id} {s.action} status={s.status} result={s.result}")


if __name__ == "__main__":
    asyncio.run(main())
