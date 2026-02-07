from typing import TypedDict, Optional, Dict, Any, List


class AgentState(TypedDict, total=False):
    # ===== runtime state ONLY =====
    agent_config: Dict[str, Any]
    goal_config: Dict[str, Any]

    plan: Optional[List[str]]
    missing_slots: Optional[List[str]]

    last_user_message: Optional[str]
    journey_status: Optional[str]

    response: Optional[str]
