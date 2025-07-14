# D:/Sirius/projects/AI_Portfolio/project7_multiAgentSDLC/streamlit_app.py

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.main import create_graph
from core.agent_state import AgentState # Import AgentState as well
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_graph()

st.set_page_config(page_title="Multi-Agent SDLC Simulator", page_icon="🤖")
st.title("🤖 Multi-Agent SDLC Simulator")
st.caption("Simulating a Software Development Agency with LLM Agents")

# Initialize the entire agent state in Streamlit's session state
if "agent_state" not in st.session_state:
    st.session_state.agent_state = AgentState(
        messages=[],
        next_action="",
        project_plan="",
        current_task={},
        completed_tasks=[],
        current_agent=""
    )

# Display chat messages from history on app rerun
for message in st.session_state.agent_state.get('messages', []):
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        # Check if the message content starts with an agent identifier
        if message.content.startswith("[") and "]:" in message.content:
            author, content = message.content.split("]:", 1)
            author = author[1:]
            with st.chat_message(author):
                st.markdown(content.strip())
        else:
            with st.chat_message("assistant"):
                st.markdown(message.content)

# Accept user input
if prompt := st.chat_input("What are your project requirements?"):
    # Add user message to the state and display it immediately
    st.session_state.agent_state['messages'].append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Determine the next agent based on the current state's next_action
    # This is a simplified mapping; in a real scenario, you might need a more robust way
    # to map next_action to the agent that will be "thinking" next.
    next_agent_name = "Project Manager" # PM is always the first to act on new input

    # Show a spinner while the agents are working
    with st.spinner(f"{next_agent_name} is thinking..."):
        # The input to the graph is the entire current agent state
        graph_input = st.session_state.agent_state
        logger.info("--- Input to Graph ---")
        # Format messages for cleaner debug output
        formatted_messages = []
        for msg in graph_input.get("messages", []):
            if isinstance(msg, HumanMessage):
                formatted_messages.append(f"Human: {msg.content[:50]}...")
            elif isinstance(msg, AIMessage):
                formatted_messages.append(f"AI: {msg.content[:50]}...")
            else:
                formatted_messages.append(f"Other: {str(msg)[:50]}...")
        graph_input_copy = {k: v for k, v in graph_input.items() if k != "messages"}
        graph_input_copy["messages"] = formatted_messages
        logger.info(f"Graph Input (messages condensed): {graph_input_copy}")

        logger.info("-----------------------------")

        # Stream the graph execution and capture the final state
        latest_state = None
        logger.info("--- Graph Stream Output ---")
        for s in app.stream(graph_input):
            logger.info(s) # Log each chunk from the stream
            # The state is the value of the node that just executed
            # We'll capture the latest one
            latest_state = s
            # Get agent node key and state
            agent_key = list(s.keys())[0]
            agent_state = s[agent_key]
            latest_messages = agent_state.get("messages", [])
            # Update the spinner message with the current agent
            if latest_messages:
                last_message = latest_messages[-1]
                if isinstance(last_message, AIMessage):
                    if last_message.content.startswith("[") and "]:" in last_message.content:
                        author, content = last_message.content.split("]:", 1)
                        author = author[1:]
                        with st.chat_message(author):
                            st.markdown(content.strip())
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(last_message.content)
            
            # Still allow spinner to show current agent thinking
            if "current_agent" in agent_state:
                current_agent_in_stream = agent_state["current_agent"]
                st.spinner(f"{current_agent_in_stream} is thinking...")

            # Exit on final state
            if "__end__" in s:
                break


        logger.info("--------------------------------")
        
        # The actual final state is the value associated with the "__end__" key
        final_state = latest_state.get("__end__") if latest_state and "__end__" in latest_state else None

        logger.info("--- Latest State Captured (after stream loop) ---")
        # Format messages for cleaner debug output
        formatted_messages_latest = []
        if latest_state and isinstance(latest_state, dict):
            # latest_state is a dictionary where keys are node names and values are the state from that node
            # We want to get the messages from the active node
            active_node_state = latest_state.get(list(latest_state.keys())[0]) if list(latest_state.keys()) else {}
            if isinstance(active_node_state, dict) and "messages" in active_node_state:
                for msg in active_node_state["messages"]:
                    if isinstance(msg, HumanMessage):
                        formatted_messages_latest.append(f"Human: {msg.content[:50]}...")
                    elif isinstance(msg, AIMessage):
                        formatted_messages_latest.append(f"AI: {msg.content[:50]}...")
                    else:
                        formatted_messages_latest.append(f"Other: {str(msg)[:50]}...")
        latest_state_copy = {k: v for k, v in (active_node_state if active_node_state else {}).items() if k != "messages"}
        latest_state_copy["messages"] = formatted_messages_latest
        logger.info(f"Latest State (messages condensed): {latest_state_copy}")

        logger.info("----------------------------------")
        logger.info("--- Final State Extracted (from latest_state) ---")
        # Format messages for cleaner debug output
        formatted_messages_final = []
        if final_state and isinstance(final_state, dict) and "messages" in final_state:
            for msg in final_state["messages"]:
                    if isinstance(msg, HumanMessage):
                        formatted_messages_final.append(f"Human: {msg.content[:50]}...")
                    elif isinstance(msg, AIMessage):
                        formatted_messages_final.append(f"AI: {msg.content[:50]}...")
                    else:
                        formatted_messages_final.append(f"Other: {str(msg)[:50]}...")
        final_state_copy = {k: v for k, v in (final_state if final_state else {}).items() if k != "messages"}
        final_state_copy["messages"] = formatted_messages_final
        logger.info(f"Final State (messages condensed): {final_state_copy}")

        logger.info("----------------------------------")

        # If the graph finished, update the session state with the final state
        if final_state:
            st.session_state.agent_state = final_state
            logger.info("--- Session State Updated with Final State ---")
            logger.info(st.session_state.agent_state)
            logger.info("-------------------------------------------------")
        # If the graph did not finish but we have a latest state (e.g., waiting for input)
        elif latest_state:
            # Find the key of the last active node
            last_node_key = list(latest_state.keys())[0]
            st.session_state.agent_state = latest_state[last_node_key]
            logger.info("--- Session State Updated with Latest State (non-final) ---")
            logger.info(st.session_state.agent_state)
            logger.info("--------------------------------------------------")
        else:
            # This can happen if the graph stops unexpectedly
            logger.warning("Graph did not yield any state.")

    # Rerun the app to display the new AI message from the updated state
    logger.info("--- Rerunning Streamlit App ---")
    st.rerun()
