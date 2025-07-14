# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/agents/project_manager.py

import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.agent_state import AgentState
from core.utils import parse_llm_response_with_action
from config.llm_config import get_llm_for_agent
from config.prompts import PROJECT_MANAGER_SYSTEM_PROMPT

def project_manager_node(state: AgentState):
    time.sleep(60) # Add a 1-minute delay
    """
    Node for the Project Manager agent.
    Handles initial requirements, task breakdown, and assignment.
    """
    state["current_agent"] = "Project Manager"
    print("[PM Node] Project Manager is processing...")
    formatted_messages = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            formatted_messages.append(f"Human: {msg.content[:50]}...")
        elif isinstance(msg, AIMessage):
            formatted_messages.append(f"AI: {msg.content[:50]}...")
        else:
            formatted_messages.append(f"Other: {str(msg)[:50]}...")
    pm_state_debug = {k: v for k, v in state.items() if k != "messages"}
    pm_state_debug["messages"] = formatted_messages
    print(f"[PM Node] State on entry (messages condensed): {pm_state_debug}")

    messages = state["messages"]
    llm = get_llm_for_agent()
    current_next_action = state.get("next_action") # Get the action that led to PM

    # Determine the context for the PM's current turn
    pm_context_message = ""
    if current_next_action == "ARCHITECT_DESIGN_COMPLETE":
        pm_context_message = "The Architect has completed the architectural design. Please review it and then break down the project into initial design and development tasks. Once ready, assign the first task to the Designer or Developer."
        # Store the architect's output as the project plan
        if messages and isinstance(messages[-1], AIMessage):
            state["project_plan"] = messages[-1].content
    elif current_next_action == "DESIGN_COMPLETE":
        pm_context_message = f"The Designer has completed the task: {state.get('current_task', {}).get('description', 'N/A')}. Please review the design and assign the next task (either development for this feature or a new design task)."
        state["completed_tasks"].append(state["current_task"]) # Mark current task as complete
        state["current_task"] = {} # Clear current task
    elif current_next_action == "DEVELOPMENT_COMPLETE":
        pm_context_message = f"The Developer has completed the task: {state.get('current_task', {}).get('description', 'N/A')}. Please review the implementation plan and assign the next task (e.g., QA, or another development task)."
        state["completed_tasks"].append(state["current_task"]) # Mark current task as complete
        state["current_task"] = {} # Clear current task
    elif current_next_action == "REQUEST_CLARIFICATION":
        pm_context_message = "Another agent has requested clarification. Please provide the necessary information or re-assign the task."
    elif current_next_action == "REQUEST_REVISION":
        pm_context_message = "You requested a revision. Please review the updated output or provide further feedback."
    else:
        pm_context_message = "Please process the client's request or continue with project management duties."


    # Construct the PM's prompt, including its system message and current context
    pm_prompt_messages = [
        SystemMessage(content=PROJECT_MANAGER_SYSTEM_PROMPT),
        HumanMessage(content=pm_context_message)
    ] + messages # Add previous conversation history

    # Invoke the LLM
    response = llm.invoke(pm_prompt_messages)

    # Parse the response for action keyword
    cleaned_content, action_keyword = parse_llm_response_with_action(response.content)

    print(f"[PM Node] PM Response: {cleaned_content}")
    print(f"[PM Node] Next Action: {action_keyword}")

    # If PM is assigning a task, try to parse it
    if action_keyword in ["ASSIGN_TO_DESIGNER", "ASSIGN_TO_DEVELOPER"]:
        # The PM should describe the task in its response.
        # We'll assume the task description is the main content of the response.
        assigned_agent_role = "designer" if action_keyword == "ASSIGN_TO_DESIGNER" else "developer"
        state["current_task"] = {
            "agent": assigned_agent_role,
            "description": cleaned_content # The PM's response is the task description
        }
        print(f"[PM Node] Assigned task to {assigned_agent_role}: {cleaned_content}")

    # Return the updated state
    updated_messages = state["messages"] + [AIMessage(content=f"[PM]: {cleaned_content}")]
    return {"messages": updated_messages, "next_action": action_keyword,
            "project_plan": state["project_plan"], "current_task": state["current_task"],
            "completed_tasks": state["completed_tasks"], "current_agent": state["current_agent"]}
