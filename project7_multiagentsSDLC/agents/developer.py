# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/agents/developer.py

import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.agent_state import AgentState
from core.utils import parse_llm_response_with_action
from config.llm_config import get_llm_for_agent
from config.prompts import DEVELOPER_SYSTEM_PROMPT

def developer_node(state: AgentState):
    time.sleep(60) # Add a 1-minute delay
    """
    Node for the Developer agent.
    Takes a task and generates an implementation plan.
    """
    state["current_agent"] = "Developer"
    print("[Developer Node] Developer is coding (planning)...")
    formatted_messages = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            formatted_messages.append(f"Human: {msg.content[:50]}...")
        elif isinstance(msg, AIMessage):
            formatted_messages.append(f"AI: {msg.content[:50]}...")
        else:
            formatted_messages.append(f"Other: {str(msg)[:50]}...")
    developer_state_debug = {k: v for k, v in state.items() if k != "messages"}
    developer_state_debug["messages"] = formatted_messages
    print(f"[Developer Node] State on entry (messages condensed): {developer_state_debug}")

    messages = state["messages"]
    llm = get_llm_for_agent()

    task_description = state.get("current_task", {}).get("description", "No specific task provided.")
    project_plan = state.get("project_plan", "No overall project plan available.")
    # Assuming the last message from the Designer (if applicable) is the design
    design_context = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and "design" in msg.content.lower(): # Simple heuristic
            design_context = f"The latest design context is: {msg.content}"
            break

    developer_context = f"Your current task is: '{task_description}'. The overall project plan/architecture is: '{project_plan}'. {design_context} Based on this, describe the technical implementation plan."

    developer_messages = [
        SystemMessage(content=DEVELOPER_SYSTEM_PROMPT),
        HumanMessage(content=developer_context)
    ] + messages # Include previous conversation for context

    response = llm.invoke(developer_messages)
    cleaned_content, action_keyword = parse_llm_response_with_action(response.content)

    print(f"[Developer Node] Developer Response: {cleaned_content}")
    print(f"[Developer Node] Next Action: {action_keyword}")

    updated_messages = state["messages"] + [AIMessage(content=f"[Developer]: {cleaned_content}")]
    return {"messages": updated_messages, "next_action": action_keyword,
            "project_plan": state["project_plan"], "current_task": state["current_task"],
            "completed_tasks": state["completed_tasks"], "current_agent": state["current_agent"]}
