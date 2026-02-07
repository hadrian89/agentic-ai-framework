import json
# from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.prompt_loader import load_prompt
from core.llm_factory import get_llm

llm = get_llm()

def planner_node(state):
    goal = state["goal_config"]

    prompt = state["agent_config"]["prompts"]["planner"].format(
        goal_description=goal["description"],
        required_slots=", ".join(goal["required_slots"])
    )

    response = llm.invoke(prompt)

    return {
        "plan": response.content,
        "journey_status": "executing",
    }
