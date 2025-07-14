# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/agents/designer.py

import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.agent_state import AgentState
from core.utils import parse_llm_response_with_action
from config.llm_config import get_llm_for_agent
from config.prompts import DESIGNER_SYSTEM_PROMPT

def designer_node(state: AgentState):
    time.sleep(60) # Add a 1-minute delay
    """
    Node for the Designer agent.
    Takes a task and generates a design description.
    """
    state["current_agent"] = "Designer"
    print("[Designer Node] Designer is working...")
    formatted_messages = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            formatted_messages.append(f"Human: {msg.content[:50]}...")
        elif isinstance(msg, AIMessage):
            formatted_messages.append(f"AI: {msg.content[:50]}...")
        else:
            formatted_messages.append(f"Other: {str(msg)[:50]}...")
    designer_state_debug = {k: v for k, v in state.items() if k != "messages"}
    designer_state_debug["messages"] = formatted_messages
    print(f"[Designer Node] State on entry (messages condensed): {designer_state_debug}")

    messages = state["messages"]
    llm = get_llm_for_agent()

    task_description = state.get("current_task", {}).get("description", "No specific task provided.")
    project_plan = state.get("project_plan", "No overall project plan available.")

    designer_context = f"Your current task is: '{task_description}'. The overall project plan/architecture is: '{project_plan}'. Based on this, describe the UI/UX design."

    designer_messages = [
        SystemMessage(content=DESIGNER_SYSTEM_PROMPT),
        HumanMessage(content=designer_context)
    ] + messages # Include previous conversation for context

    response = llm.invoke(designer_messages)
    cleaned_content, action_keyword = parse_llm_response_with_action(response.content)

    print(f"[Designer Node] Designer Response: {cleaned_content}")
    print(f"[Designer Node] Next Action: {action_keyword}")

    updated_messages = state["messages"] + [AIMessage(content=f"[Designer]: {cleaned_content}")]
    return {"messages": updated_messages, "next_action": action_keyword,
            "project_plan": state["project_plan"], "current_task": state["current_task"],
            "completed_tasks": state["completed_tasks"], "current_agent": state["current_agent"]}
