import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.prompt_loader import load_prompt
from core.llm_factory import get_llm
llm = get_llm()


def responder_node(state: AgentState) -> AgentState:
    prompt = load_prompt(
        state["agent_config"]["prompts"]["summary"],
        {
            "tool_result": json.dumps(state.get("tool_result", {}), indent=2),
            "collected_slots": json.dumps(state.get("collected_slots", {}), indent=2),
        }
    )

    response = llm.invoke([
        SystemMessage(content="You must only summarise provided data."),
        HumanMessage(content=prompt),
    ])

    # state["messages"].append({
    #     "role": "assistant",
    #     "content": response.content.strip()
    # })

    # return state
    return {
        "response": response
    }
