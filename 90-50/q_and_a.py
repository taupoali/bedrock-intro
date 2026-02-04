import json
import os
from pathlib import Path

import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

BASE_DIR = Path(__file__).parent
text = (BASE_DIR / "aws_incident.txt").read_text(encoding="utf-8")

question = "How long did this incident last?"

prompt = (
    "You are a question-answering assistant.\n"
    "Answer the question using ONLY the incident report below.\n"
    "If the answer is not explicitly stated, reply exactly with:\n"
    "Not found in provided text.\n"
    "Be concise (1-3 sentences).\n"
    "\n"
    "INCIDENT REPORT:\n"
    f"{text}\n"
    "\n"
    "QUESTION:\n"
    f"{question}"
)

client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 250,
    "temperature": 0.0,
    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
}

response = client.invoke_model(
    modelId=MODEL_ID,
    body=json.dumps(body),
    accept="application/json",
    contentType="application/json",
)

payload = json.loads(response["body"].read())
print(payload["content"][0]["text"])
