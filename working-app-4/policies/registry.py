from policies.sufficient_balance import sufficient_balance
from policies.daily_limit import daily_limit
from policies.aml import aml_check

POLICY_REGISTRY = {
    "sufficient_balance": sufficient_balance,
    "daily_limit": daily_limit,
    "aml_check": aml_check,
}
