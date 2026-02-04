import boto3
import json
from pathlib import Path

client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "amazon.nova-micro-v1:0"

def analyze_sentiment(review: str):
    prompt = f"""
Instruction:
You are a sentiment analysis assistant for product feedback.

Requirements:
- Return JSON only (no extra text)
- Use these labels only: "positive", "negative", "neutral", "mixed"
- Provide:
  - sentiment
  - confidence (0 to 1)

Input:
{review}
"""

    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 120,
            "temperature": 0.0,
            "topP": 0.9
        }
    )

    text = response["output"]["message"]["content"][0]["text"]
    return json.loads(text)


# --- Read reviews from file ---
reviews = []

BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "customer_reviews.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            # Remove leading numbering (e.g. "1. ")
            review = line.split(".", 1)[1].strip()
            reviews.append(review)


# --- Analyze each review ---
results = []

for review in reviews:
    data = analyze_sentiment(review)
    results.append((review, data["sentiment"], data["confidence"]))


# --- Print results ---
for review, sentiment, confidence in results:
    print(f"- {sentiment:8} ({confidence:.2f})  {review}")
