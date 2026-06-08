# import base64
# from g4f.client import Client

# # 1. Read and base64‑encode your image file
# if __name__ == "__main__":
#     image_path = "C:\\Users\\2010436\\OneDrive - Northshore School District\\Documents\\GitHub\\c.o.r.i\\aiCode\\images\\Screenshot 2026-05-18 135651.png"  # change to your file
#     with open(image_path, "rb") as f:
#         image_bytes = f.read()

#     image_b64 = base64.b64encode(image_bytes).decode("utf-8")

#     # 2. Build the message with text + image
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Here is an image. imagine you are a robotic arm looking at this image. based on your position, Only create a 3d vector pointing to the object in the image, approzimate the z axis. the X axis is the width of the image and the Y axis is the height of the image. The Z axis is determined based on how far away the object is.",
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         # For local files, use a data URL with base64
#                         "url": f"data:image/png;base64,{image_b64}",
#                     },
#                 },
#             ],
#         }
#     ]

#     # 3. Call g4f with gpt-4o-mini
#     client = Client()
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         web_search=False,
#     )


#     # 4. Print the generated code / answer
#     print(response.choices[0].message.content)
from ai4free import LEO
from Helpingai_T2 import Perplexity
# Experimental AI test script — quick playpen for chat/image helpers.
leo = LEO()
# Print model reply for a basic sanity check
print(leo.chat("Hello"))