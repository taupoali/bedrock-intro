import os
from pathlib import Path

import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.meta.llama3-2-3b-instruct-v1:0")

BASE_DIR = Path(__file__).parent
text = (BASE_DIR / "aws_incident.txt").read_text(encoding="utf-8")

prompt = (
    "You are a careful technical summarizer.\n"
    "Summarize the incident report below.\n"
    "Constraints:\n"
    "- Use exactly 5 bullet points\n"
    "- Each bullet must be 1 sentence\n"
    "- Only use information present in the report\n"
    "- Audience: technical manager\n"
    "\n"
    "INCIDENT REPORT:\n"
    f"{text}"
)

client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

response = client.converse(
    modelId=MODEL_ID,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
    inferenceConfig={"maxTokens": 500, "temperature": 0.2}
)

print(response["output"]["message"]["content"][0]["text"])
