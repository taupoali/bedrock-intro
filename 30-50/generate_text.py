import json
import boto3

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-lite-v1:0"  # If your catalog shows a different ID, use that.

brt = boto3.client("bedrock-runtime", region_name=REGION)

prompt = "Explain what Amazon Bedrock is in 2 short bullet points."

body = {
    "schemaVersion": "messages-v1",
    "messages": [
        {"role": "user", "content": [{"text": prompt}]}
    ],
    "inferenceConfig": {
        "maxTokens": 200,
        "temperature": 0.5
    }
}

response = brt.invoke_model(
    modelId=MODEL_ID,
    body=json.dumps(body),
)

result = json.loads(response["body"].read())

# Nova-style responses contain content blocks; grab the text blocks.
text_out = ""
for block in result.get("output", {}).get("message", {}).get("content", []):
    if "text" in block:
        text_out += block["text"]

print(text_out.strip())
