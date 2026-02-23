import os
from pathlib import Path

import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.meta.llama3-2-3b-instruct-v1:0")

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

response = client.converse(
    modelId=MODEL_ID,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
    inferenceConfig={"maxTokens": 250, "temperature": 0.0}
)

print(response["output"]["message"]["content"][0]["text"])
