import base64
from g4f.client import Client

# Read and base64‑encode the image
with open("my_image.png.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

client = Client()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}"
                    }
                },
            ],
        },
    ],
)

print(response.choices[0].message.content)

from g4f.client import Client
from g4f.Provider import SomeFreeProvider  # example name, check docs

client = Client()

response = client.chat.completions.create(
    model="gpt-4o-mini",  # or whatever that provider supports
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image."},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image.png"},
                },
            ],
        },
    ],
    provider=SomeFreeProvider,
)

print(response.choices[0].message.content)