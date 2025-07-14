import os
from llama_index.llms.openai import OpenAI

OPENAI_API_KEY = 'env'
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

openai_llm = OpenAI(model='gpt-4o')

from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt

from llama_index.core.llms import (
    ChatMessage,
    ImageBlock,
    TextBlock,
    MessageRole,
)


image_urls = [
    "https://res.cloudinary.com/hello-tickets/image/upload/c_limit,f_auto,q_auto,w_1920/v1640835927/o3pfl41q7m5bj8jardk0.jpg",
    "https://www.visualcapitalist.com/wp-content/uploads/2023/10/US_Mortgage_Rate_Surge-Sept-11-1.jpg",
    "https://i2-prod.mirror.co.uk/incoming/article7160664.ece/ALTERNATES/s1200d/FIFA-Ballon-dOr-Gala-2015.jpg",
]

import asyncio

async def process_images():
    for image_url in image_urls:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        plt.imshow(img)
        # plt.show()
        msg = ChatMessage(
            role=MessageRole.USER,
            blocks=[
                TextBlock(text="Describe the images as an alternative text"),
                ImageBlock(url=image_url),
            ],
        )
        # sync chat
        # response = openai_llm.chat(messages=[msg])
        # print(response)
        async_resp = await openai_llm.astream_chat(messages=[msg])
        async for delta in async_resp:
            print(delta.delta, end="")

if __name__ == "__main__":
    asyncio.run(process_images())
