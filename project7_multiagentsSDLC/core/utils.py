# D:/Sirius/projects/AI_Portfolio/project7_multiagentsSDLC/core/utils.py

def parse_llm_response_with_action(response_content: str) -> (str, str):
    action_keyword = "NO_ACTION_SPECIFIED"
    cleaned_content = response_content
    if "[ACTION:" in response_content:
        start_index = response_content.find("[ACTION:")
        end_index = response_content.find("]", start_index)
        if end_index != -1:
            action_keyword = response_content[start_index + len("[ACTION:"):end_index].strip().upper()
            cleaned_content = response_content[:start_index].strip()
    return cleaned_content, action_keyword
