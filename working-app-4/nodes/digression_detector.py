from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.prompt_loader import load_prompt
from core.llm_factory import get_llm
llm = get_llm()


# def digression_detector_node(state: AgentState) -> AgentState:
#     prompt = load_prompt(
#         state["agent_config"]["prompts"]["digression_classifier"],
#         {
#             "goal_description": state["goal_config"]["description"],
#             "required_slots": state["required_slots"],
#             "missing_slots": state["missing_slots"],
#             "user_message": state["last_user_message"],
#         }
#     )

#     response = llm.invoke([
#         SystemMessage(content="Classify only. No explanation."),
#         HumanMessage(content=prompt),
#     ])

#     classification = response.content.strip()

#     if classification == "DIGRESSION":
#         state["digression_detected"] = True
#     else:
#         state["digression_detected"] = False

#     state["last_classification"] = classification

#     return state
def digression_detector_node(state):
    prompts = state["agent_config"].get("prompts", {})

    digression_prompt = prompts.get("digression_classifier")

    # ✅ If no digression prompt defined, skip detection
    if not digression_prompt:
        state["digression_detected"] = False
        return state

    # (Later you can plug LLM logic here)
    # For now keep it deterministic
    state["digression_detected"] = False
    return state
