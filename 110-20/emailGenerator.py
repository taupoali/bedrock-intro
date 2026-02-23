import json
import boto3

REGION = "us-east-1"
MODEL_ID = "us.meta.llama3-2-3b-instruct-v1:0"

brt = boto3.client("bedrock-runtime", region_name=REGION)

def build_prompt(data: dict) -> str:
    # Keep it explicit for learner clarity
    return f"""
Instruction:
You are a marketing copywriter. Write a marketing email.

Requirements:
- Output JSON only (no markdown, no extra text)
- Use UK English
- Avoid spammy language (no "FREE!!!", no excessive emojis)
- Create:
  - subject_lines: array of 3 subject lines (max 60 chars each)
  - preheader: string (max 90 chars)
  - email_body: string (150-220 words, includes greeting, value proposition, social proof placeholder, and CTA)
  - cta: string (short action phrase)

Input:
product_name: {data["product_name"]}
product_description: {data["product_description"]}
audience: {data["audience"]}
goal: {data["goal"]}
tone: {data["tone"]}
length: {data["length"]}
""".strip()

def lambda_handler(event, context):
    # API Gateway proxy sends body as a string
    try:
        # Case 1: API Gateway proxy event
        if "body" in event:
            body = event["body"]
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body

        # Case 2: Direct Lambda test invocation
        else:
            data = event

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Request body must be valid JSON"})
        }

    required_fields = ["product_name", "product_description", "audience", "goal", "tone", "length"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Missing required fields: {', '.join(missing)}"})
        }

    prompt = build_prompt(data)

    resp = brt.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 500, "temperature": 0.3, "topP": 0.9}
    )

    text = resp["output"]["message"]["content"][0]["text"]

    # Ensure the model returned valid JSON
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"statusCode": 502, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Model returned non-JSON output", "raw": text})}

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            # CORS is needed for Lab B (browser frontend)
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(payload)
    }
