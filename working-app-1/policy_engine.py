# """
# policy_engine.py
# Simple PolicyEngine that loads JSON policy files and enforces rules.
# """

# import json
# from typing import Any, Dict, List

# class PolicyViolation(Exception):
#     pass

# class PolicyEngine:
#     def __init__(self, policy_files: List[str]):
#         self.rules = []
#         for p in policy_files:
#             with open(p, "r") as fh:
#                 data = json.load(fh)
#                 self.rules.extend(data.get("rules", []))

#     def enforce(self, tool_name: str, params: Dict[str, Any]) -> None:
#         for rule in self.rules:
#             if rule.get("tool") != tool_name:
#                 continue

#             # max_amount
#             if "max_amount" in rule and "amount" in params:
#                 if params.get("amount", 0) > rule["max_amount"]:
#                     raise PolicyViolation(f"Amount {params.get('amount')} exceeds policy max of {rule['max_amount']}")

#             # allowed currencies
#             if "allowed_currencies" in rule and "currency" in params:
#                 if params.get("currency") not in rule["allowed_currencies"]:
#                     raise PolicyViolation(f"Currency {params.get('currency')} not allowed for tool {tool_name}")

#             # requires_approval
#             if rule.get("requires_approval") and not params.get("approved", False):
#                 raise PolicyViolation(f"Approval required for {tool_name} — set 'approved': true")
