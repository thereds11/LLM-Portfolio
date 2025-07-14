# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/agents/architect.py

import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.agent_state import AgentState
from core.utils import parse_llm_response_with_action
from config.llm_config import get_llm_for_agent
from config.prompts import ARCHITECT_SYSTEM_PROMPT

def architect_node(state: AgentState):
    time.sleep(60) # Add a 1-minute delay
    """
    Node for the Architect agent.
    Receives project details and generates an architectural design.
    """
    state["current_agent"] = "Architect"
    print("[Architect Node] Architect is designing...")
    formatted_messages = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            formatted_messages.append(f"Human: {msg.content[:50]}...")
        elif isinstance(msg, AIMessage):
            formatted_messages.append(f"AI: {msg.content[:50]}...")
        else:
            formatted_messages.append(f"Other: {str(msg)[:50]}...")
    architect_state_debug = {k: v for k, v in state.items() if k != "messages"}
    architect_state_debug["messages"] = formatted_messages
    print(f"[Architect Node] State on entry (messages condensed): {architect_state_debug}")

    messages = state["messages"]
    llm = get_llm_for_agent()

    # Ensure the Architect's system message is at the beginning for its turn
    architect_messages = [SystemMessage(content=ARCHITECT_SYSTEM_PROMPT)] + messages

    # Invoke the LLM
    response = llm.invoke(architect_messages)

    # Parse the response for action keyword
    cleaned_content, action_keyword = parse_llm_response_with_action(response.content)

    print(f"[Architect Node] Architect Response: {cleaned_content}")
    print(f"[Architect Node] Next Action: {action_keyword}")

    # Return the updated state
    updated_messages = state["messages"] + [AIMessage(content=f"[Architect]: {cleaned_content}")]
    return {"messages": updated_messages, "next_action": action_keyword,
            "project_plan": state["project_plan"], "current_task": state["current_task"],
            "completed_tasks": state["completed_tasks"], "current_agent": state["current_agent"]}
