
import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import numpy as np  # Required for byte conversion
import time
from openai import OpenAI
import os
import requests
# Optional: Only import display if in Jupyter
# try:
#     # from IPython.display import display, Image
#     # JUPYTER = True
# except ImportError:
JUPYTER = False

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
video = cv2.VideoCapture("playback.mp4")

base64Frames = []
while video.isOpened():
    success, frame = video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

video.release()
print(len(base64Frames), "frames read.")

# Handle different environments
for img in base64Frames:
    img_bytes = base64.b64decode(img)  # Decode Base64 to raw bytes
    np_array = np.frombuffer(img_bytes, dtype=np.uint8)  # Convert bytes to NumPy array
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # Decode image

    # frame = cv2.imdecode(
    #     base64.b64decode(img.encode("utf-8")), cv2.IMREAD_COLOR
    # )
    if frame is None:
        print("Error decoding frame, skipping...")
        continue

    cv2.imshow("Video Frame", frame)
    if cv2.waitKey(25) & 0xFF == ord("q"):  # Press 'q' to exit
        break
cv2.destroyAllWindows()

PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video.",
            *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
        ],
    },
]
params = {
    "model": "gpt-4o",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 200,
}

result = client.chat.completions.create(**params)
print(result.choices[0].message.content)