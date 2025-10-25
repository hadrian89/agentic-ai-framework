# """
# agentic_framework.py
# Core classes: Planner, ExecutionNode, MonitorNode, Replanner, Agent, plus mock tools.
# Designed to be self-contained and easy to extend.
# """

# import asyncio
# import json
# import re
# from dataclasses import dataclass, field
# from typing import Any, Callable, Dict, List, Optional

# # ----- LLM wrapper that will use Ollama if available, else fallback to MockLLM -----
# class MockLLM:
#     """Simple deterministic mock LLM for testing and local runs without Ollama."""
#     def __init__(self, model_name: str = "mock"):
#         self.model_name = model_name

#     def generate_text(self, prompt: str) -> str:
#         # Very simple heuristics to respond with JSON plans for our demo prompts.
#         # For production, replace with actual LLM (Ollama client or OpenAI).
#         if "Create a minimal step-by-step plan" in prompt or "Plan steps to achieve the goal" in prompt:
#             # produce a small JSON plan depending on keywords
#             if "payment" in prompt.lower():
#                 return json.dumps({
#                     "goal": "Make a payment",
#                     "steps": [
#                         {"id": "s1", "action": "make_payment", "params": {"from_account": "A-123", "to_account": "B-987", "amount": 150.0, "currency": "GBP", "approved": True}},
#                         {"id": "s2", "action": "confirm_transaction", "params": {}}
#                     ]
#                 })
#             elif "statement" in prompt.lower():
#                 return json.dumps({
#                     "goal": "Get statement",
#                     "steps": [
#                         {"id": "s1", "action": "get_statement", "params": {"account_id": "A-123", "months": 1}},
#                         {"id": "s2", "action": "summarize_statement", "params": {}}
#                     ]
#                 })
#             else:
#                 return json.dumps({
#                     "goal": "Generic goal",
#                     "steps": [
#                         {"id": "s1", "action": "noop", "params": {}}
#                     ]
#                 })
#         # replanner heuristic
#         if "replan" in prompt.lower() or "one step failed" in prompt.lower():
#             return json.dumps({
#                 "goal": "Replanned goal",
#                 "steps": [
#                     {"id": "r1", "action": "make_payment", "params": {"from_account": "A-123", "to_account": "B-987", "amount": 100.0, "currency": "GBP", "approved": True}}
#                 ]
#             })
#         # default fallback
#         return "OK"

# try:
#     # Try to import ollama client if present
#     import ollama  # type: ignore

#     class OllamaLLM:
#         def __init__(self, model_name: str = "llama3"):
#             self.model_name = model_name
#             self.client = ollama.Ollama()  # connects to local ollama server

#         def generate_text(self, prompt: str) -> str:
#             # `generate` returns an object — adapt depending on installed client API.
#             res = self.client.generate(self.model_name, prompt)
#             # The structure may differ depending on ollama client; try common attributes:
#             if hasattr(res, "text"):
#                 return res.text
#             if isinstance(res, dict) and "text" in res:
#                 return res["text"]
#             return str(res)

#     DefaultLLM = OllamaLLM

# except Exception:
#     # Ollama not installed or import failed; use mock
#     DefaultLLM = MockLLM


# # -------------------------
# # Mock tools (replace with real bank clients in prod)
# # -------------------------
# async def mock_make_payment(from_account: str, to_account: str, amount: float, currency: str = "GBP", approved: bool = False) -> Dict[str, Any]:
#     """Simulate a payment tool. Fails when amount > 1000 to demonstrate replanning."""
#     await asyncio.sleep(0.2)
#     if not approved:
#         return {"status": "failed", "reason": "approval_required"}
#     if amount > 1000:
#         return {"status": "failed", "reason": "amount_exceeds_authorization_limit"}
#     return {"status": "success", "transaction_id": f"TXN-{int(amount*1000)}"}

# async def mock_get_statement(account_id: str, months: int = 1) -> Dict[str, Any]:
#     await asyncio.sleep(0.1)
#     return {
#         "status": "success",
#         "account_id": account_id,
#         "months": months,
#         "transactions": [
#             {"id": "t1", "amount": -12.5, "desc": "Coffee"},
#             {"id": "t2", "amount": -40.0, "desc": "Grocery"},
#         ]
#     }

# async def mock_confirm_transaction():
#     await asyncio.sleep(0.05)
#     return {"status": "success", "message": "confirmed"}


# # -------------------------
# # Core dataclasses and nodes
# # -------------------------
# @dataclass
# class Step:
#     id: str
#     action: str
#     params: Dict[str, Any]
#     status: str = "pending"
#     result: Optional[Dict[str, Any]] = None

# @dataclass
# class Plan:
#     goal: str
#     steps: List[Step] = field(default_factory=list)
#     metadata: Dict[str, Any] = field(default_factory=dict)


# class Planner:
#     """LLM-driven planner that returns a Plan from a goal."""
#     def __init__(self, llm: Optional[Any] = None):
#         self.llm = llm or DefaultLLM()

#     async def create_plan(self, goal: str, context: Dict[str, Any] = None) -> Plan:
#         ctx = context or {}
#         prompt = (
#             "Create a minimal step-by-step plan (as strict JSON) to achieve the goal.\n"
#             f"Goal: {goal}\nContext: {json.dumps(ctx)}\n"
#             "Return ONLY JSON with top-level object containing 'goal' and 'steps' (each step has id, action, params)."
#         )
#         # run LLM in a thread to avoid blocking event loop if LLM is synchronous
#         raw = await asyncio.to_thread(self.llm.generate_text, prompt)
#         payload = self._parse_json_fallback(raw)
#         steps = [Step(id=s.get("id"), action=s.get("action"), params=s.get("params", {})) for s in payload.get("steps", [])]
#         return Plan(goal=payload.get("goal", goal), steps=steps, metadata={"llm_raw": raw})

#     def _parse_json_fallback(self, raw: str) -> Dict[str, Any]:
#         try:
#             return json.loads(raw)
#         except Exception:
#             m = re.search(r"\{.*\}", raw, re.DOTALL)
#             if m:
#                 return json.loads(m.group(0))
#             raise


# class ExecutionNode:
#     """Executes Step objects using registered tools. Integrates PolicyEngine optionally."""
#     def __init__(self, policy_engine: Optional[Any] = None):
#         self.tools: Dict[str, Callable[..., Any]] = {}
#         self.policy_engine = policy_engine

#         # register built-in mock tools (can be overridden)
#         self.register_tool("make_payment", mock_make_payment)
#         self.register_tool("get_statement", mock_get_statement)
#         self.register_tool("confirm_transaction", mock_confirm_transaction)

#     def register_tool(self, name: str, fn: Callable[..., Any]):
#         self.tools[name] = fn

#     async def execute_step(self, step: Step) -> Step:
#         step.status = "running"
#         tool = self.tools.get(step.action)
#         if not tool:
#             step.status = "failed"
#             step.result = {"status": "failed", "reason": f"unknown_tool:{step.action}"}
#             return step

#         try:
#             # policy check (synchronous raise if violated)
#             if self.policy_engine:
#                 self.policy_engine.enforce(step.action, step.params)

#             # call the tool (support coroutine or regular function)
#             if asyncio.iscoroutinefunction(tool):
#                 res = await tool(**step.params)
#             else:
#                 # run blocking tool in thread
#                 res = await asyncio.to_thread(tool, **step.params)
#             step.result = res
#             step.status = "success" if isinstance(res, dict) and res.get("status") == "success" else "failed"
#         except Exception as e:
#             step.status = "failed"
#             step.result = {"status": "failed", "reason": str(e)}
#         return step


# class MonitorNode:
#     """Records and emits execution events."""
#     def __init__(self):
#         self.history: List[Dict[str, Any]] = []

#     async def observe(self, step: Step):
#         rec = {"id": step.id, "action": step.action, "status": step.status, "result": step.result}
#         self.history.append(rec)
#         # simple logging — in real system push metrics/logs
#         print(f"[Monitor] step={step.id} action={step.action} status={step.status} result={step.result}")


# class Replanner:
#     """Invokes LLM to produce a revised plan when a step fails."""
#     def __init__(self, llm: Optional[Any] = None):
#         self.llm = llm or DefaultLLM()

#     async def replan(self, failed_step: Step, current_plan: Plan, context: Dict[str, Any] = None) -> Plan:
#         ctx = context or {}
#         prompt = (
#             "You are a replanner. One step failed. "
#             f"Goal: {current_plan.goal}\n"
#             f"Failed step: {json.dumps({'id': failed_step.id,'action': failed_step.action,'params': failed_step.params,'result': failed_step.result})}\n"
#             f"Current plan steps: {json.dumps([{'id':s.id,'action':s.action,'params':s.params,'status':s.status} for s in current_plan.steps])}\n"
#             "Suggest a revised plan (JSON) to complete the goal. Return JSON with 'goal' and 'steps'."
#         )
#         raw = await asyncio.to_thread(self.llm.generate_text, prompt)
#         payload = self._parse_json_fallback(raw)
#         steps = [Step(id=s.get("id"), action=s.get("action"), params=s.get("params", {})) for s in payload.get("steps", [])]
#         return Plan(goal=payload.get("goal", current_plan.goal), steps=steps, metadata={"llm_raw": raw})

#     def _parse_json_fallback(self, raw: str) -> Dict[str, Any]:
#         try:
#             return json.loads(raw)
#         except Exception:
#             m = re.search(r"\{.*\}", raw, re.DOTALL)
#             if m:
#                 return json.loads(m.group(0))
#             raise


# class Agent:
#     """High-level agent encapsulating Planner, ExecutionNode, MonitorNode, Replanner."""
#     def __init__(self, name: str, planner: Planner, exec_node: ExecutionNode, monitor: MonitorNode, replanner: Replanner, meta: Dict[str, Any] = None):
#         self.name = name
#         self.planner = planner
#         self.exec_node = exec_node
#         self.monitor = monitor
#         self.replanner = replanner
#         self.meta = meta or {}

#     async def run_goal(self, goal: str, context: Dict[str, Any] = None) -> Plan:
#         print(f"[{self.name}] creating plan for goal: {goal}")
#         plan = await self.planner.create_plan(goal, context or {})
#         # execute steps in order
#         for step in plan.steps:
#             print(f"[{self.name}] executing step {step.id} -> {step.action}")
#             step = await self.exec_node.execute_step(step)
#             await self.monitor.observe(step)
#             if step.status != "success":
#                 print(f"[{self.name}] step {step.id} failed with reason: {step.result}")
#                 # replan
#                 new_plan = await self.replanner.replan(step, plan, context or {})
#                 print(f"[{self.name}] replanner returned {len(new_plan.steps)} steps. Restarting with replanned plan.")
#                 # For simplicity, restart execution with the new plan
#                 return await self.run_goal(new_plan.goal, context)
#         print(f"[{self.name}] plan completed successfully")
#         return plan
