from pathlib import Path
import shutil
from app import image_urls
from llama_index.core.llms import (
    ChatMessage,
    ImageBlock,
    TextBlock,
    MessageRole,
)
from app import openai_llm

import requests

img_path = Path().resolve() / "image.jpg"
response = requests.get(image_urls[-1])
with open(img_path, "wb") as file:
    file.write(response.content)

msg = ChatMessage(
    role=MessageRole.USER,
    blocks=[
        TextBlock(text="Describe the image as an alternative text"),
        ImageBlock(path=img_path, image_mimetype="image/jpeg"),
    ],
)

response = openai_llm.chat(messages=[msg])
print(response)