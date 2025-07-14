# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/graph/router.py

from langchain_core.messages import HumanMessage, AIMessage
from core.agent_state import AgentState
from langgraph.graph import END

def route_agent(state: AgentState):
    """
    Routes the flow based on the 'next_action' in the state.
    """
    next_action = state.get("next_action")
    print(f"[Router] Routing based on next_action: {next_action}")
    formatted_messages = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            formatted_messages.append(f"Human: {msg.content[:50]}...")
        elif isinstance(msg, AIMessage):
            formatted_messages.append(f"AI: {msg.content[:50]}...")
        else:
            formatted_messages.append(f"Other: {str(msg)[:50]}...")
    router_state_debug = {k: v for k, v in state.items() if k != "messages"}
    router_state_debug["messages"] = formatted_messages
    print(f"[Router] Current state (messages condensed): {router_state_debug}")


    if next_action == "HANDOFF_TO_ARCHITECT":
        print("[Router] Routing to Architect for design.")
        return "architect_node"
    elif next_action == "ARCHITECT_DESIGN_COMPLETE":
        print("[Router] Architect design complete. Routing back to Project Manager for review and task breakdown.")
        return "project_manager"
    elif next_action == "INITIAL_PLANNING_COMPLETE":
        print("[Router] Initial planning complete. Routing to Project Manager for task breakdown.")
        return "project_manager" # PM will now break down tasks
    elif next_action == "ASSIGN_TO_DESIGNER":
        print("[Router] Project Manager assigned task to Designer.")
        return "designer_node"
    elif next_action == "DESIGN_COMPLETE":
        print("[Router] Designer task complete. Routing back to Project Manager for review and next assignment.")
        return "project_manager"
    elif next_action == "ASSIGN_TO_DEVELOPER":
        print("[Router] Project Manager assigned task to Developer.")
        return "developer_node"
    elif next_action == "DEVELOPMENT_COMPLETE":
        print("[Router] Developer task complete. Routing back to Project Manager for review and next assignment.")
        return "project_manager"
    elif next_action == "PHASE_COMPLETE":
        print("[Router] Project Manager declared phase complete. Ending this phase.")
        return END
    elif next_action == "CLARIFY_CLIENT_INPUT":
        print("[Router] Project Manager needs clarification. Ending graph run to wait for client input.")
        return END # Stop the graph and wait for the user to respond in the UI.
    elif next_action == "REQUEST_CLARIFICATION":
        print("[Router] Agent requested clarification. Routing back to Project Manager (PM to clarify/re-assign).")
        return "project_manager"
    elif next_action == "REQUEST_REVISION":
        print("[Router] Project Manager requested revision. Routing back to Project Manager (agent to revise).")
        return "project_manager"
    else:
        # Fallback for unexpected actions or if the LLM didn't follow instructions
        print(f"[Router] Unexpected action: {next_action}. Defaulting to Project Manager.")
        return "project_manager" # Default to PM to handle or clarify
