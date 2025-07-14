# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/core/agent_state.py

from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

# 1. Define the Graph State
class AgentState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: A list of messages exchanged in the conversation.
        next_action: A string indicating the next action or agent to route to.
        project_plan: A string representing the overall project plan/architecture.
        current_task: A dictionary representing the task currently being worked on.
                      e.g., {"agent": "designer", "description": "Design login page"}
        completed_tasks: A list of dictionaries for completed tasks.
        current_agent: A string representing the agent currently working.
    """
    messages: Annotated[List[BaseMessage], lambda x, y: x + y] # Appends new messages
    next_action: str
    project_plan: str # To store the high-level plan/architecture
    current_task: Dict # To store details of the current task
    completed_tasks: Annotated[List[Dict], lambda x, y: x + y] # List of completed tasks
    current_agent: str
