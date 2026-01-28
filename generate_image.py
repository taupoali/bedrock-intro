import base64
import json
import random
import boto3

REGION = "us-east-1"
MODEL_ID = "amazon.nova-canvas-v1:0"

client = boto3.client("bedrock-runtime", region_name=REGION)

prompt = "A cartoon frog doing a high jump at a full stadium at the olympic games."

seed = random.randint(0, 858_993_460)

body = {
    "taskType": "TEXT_IMAGE",
    "textToImageParams": {"text": prompt},
    "imageGenerationConfig": {
        "seed": seed,
        "quality": "standard",
        "height": 512,
        "width": 512,
        "numberOfImages": 1
    }
}

response = client.invoke_model(
    modelId=MODEL_ID,
    body=json.dumps(body),
)

result = json.loads(response["body"].read())

# The response returns base64-encoded PNG(s)
image_b64 = result["images"][0]
image_bytes = base64.b64decode(image_b64)

output_file = "nova_canvas.png"
with open(output_file, "wb") as f:
    f.write(image_bytes)

print(f"Saved image to {output_file}")
