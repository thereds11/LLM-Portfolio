# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/config/llm_config.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM for the agents
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)

def get_llm_for_agent():
    """
    Returns the initialized LLM instance.
    We'll pass the system message when invoking the LLM within the graph.
    """
    return llm
