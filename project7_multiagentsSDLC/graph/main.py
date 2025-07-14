# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/graph/main.py

from langgraph.graph import StateGraph, END
from core.agent_state import AgentState
from agents.project_manager import project_manager_node
from agents.architect import architect_node
from agents.designer import designer_node
from agents.developer import developer_node
from graph.router import route_agent
from langchain_core.messages import HumanMessage


def create_graph():
    # Build the Graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("project_manager", project_manager_node)
    workflow.add_node("architect_node", architect_node)
    workflow.add_node("designer_node", designer_node)
    workflow.add_node("developer_node", developer_node)

    # Set the entry point
    workflow.set_entry_point("project_manager")

    # Add conditional edges from Project Manager
    workflow.add_conditional_edges(
        "project_manager", # From this node
        route_agent,       # Use this function to decide next
        {
            "architect_node": "architect_node",
            "designer_node": "designer_node",
            "developer_node": "developer_node",
            "project_manager": "project_manager", # Loop back to PM for clarification, revision, or next task
            END: END
        }
    )

    # Add conditional edges from Architect
    workflow.add_conditional_edges(
        "architect_node", # From this node
        route_agent,       # Use this function to decide next
        {
            "project_manager": "project_manager", # Architect hands back to PM or requests clarification from PM
            END: END # Architect should not directly end the graph, but included for completeness
        }
    )

    # Add conditional edges from Designer
    workflow.add_conditional_edges(
        "designer_node", # From this node
        route_agent,       # Use this function to decide next
        {
            "project_manager": "project_manager", # Designer hands back to PM or requests clarification
            END: END
        }
    )

    # Add conditional edges from Developer
    workflow.add_conditional_edges(
        "developer_node", # From this node
        route_agent,       # Use this function to decide next
        {
            "project_manager": "project_manager", # Developer hands back to PM or requests clarification
            END: END
        }
    )

    # Compile the graph
    app = workflow.compile()
    return app

# --- How to run the graph (for testing) ---
if __name__ == "__main__":
    app = create_graph()
    # Example of how to invoke the graph with initial user input
    initial_input = "I need a web application that allows users to create and manage personal to-do lists. It should have user authentication, CRUD operations for tasks, and a simple, intuitive UI."

    # The initial state for the graph
    inputs = {"messages": [HumanMessage(content=initial_input)], "project_plan": "", "current_task": {}, "completed_tasks": []}

    # Run the graph
    for s in app.stream(inputs):
        print(s)
