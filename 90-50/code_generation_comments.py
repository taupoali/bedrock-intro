import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "amazon.nova-micro-v1:0"

prompt = f"""
Instruction:
You are a beginner Python developer.

Requirements:
- Return code only
- Provide clear comments
- Define a function named find_biggest
- Use simple syntax
- The function should return the biggest number
- Use blank lines where appropriate to improve readability

Input:
Write a Python function that finds the biggest number in a list.

"""

resp = client.converse(
    modelId=model_id,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
    inferenceConfig={"maxTokens": 200, "temperature": 0.0, "topP": 0.9}
)

text = resp["output"]["message"]["content"][0]["text"]
print(text)


