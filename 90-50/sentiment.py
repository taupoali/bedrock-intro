import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "us.meta.llama3-2-3b-instruct-v1:0"

review = "Great… arrived broken. Really impressed."

prompt = f"""
Instruction:
You are a sentiment analysis assistant for product feedback.

Requirements:
- Return JSON only (no extra text)
- Use these labels only: "positive", "negative", "neutral", "mixed"
- Provide:
  - sentiment (one of the labels)
  - confidence (0 to 1)
  - key_phrases (array of 1 to 3 short phrases from the text)
  - rationale (one short sentence, max 20 words)

Input:
{review}
"""

resp = client.converse(
    modelId=model_id,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
    inferenceConfig={"maxTokens": 200, "temperature": 0.0, "topP": 0.9}
)

text = resp["output"]["message"]["content"][0]["text"]
print(text)

# Optional: validate JSON (helps learners see why structured outputs matter)
data = json.loads(text)
print("\nParsed sentiment:", data["sentiment"])
