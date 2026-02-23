import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "us.meta.llama3-2-3b-instruct-v1:0"

prompt = f"""
Instruction:
You are a Python developer.

Requirements:
- Return code only
- No explanations or comments
- Define a function named find_biggest
- The function should return the biggest number

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


