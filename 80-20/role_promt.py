import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "amazon.nova-micro-v1:0"

prompt = """
Instruction:
You are an in house lawyer who is drafting an organizational risk assessment.

Input:
Explain Amazon VPC by:
1. Describing what it is
2. Explaining why it exists
3. Giving one real-world example

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
        "maxTokens": 800,
        "temperature": 0.3,
        "topP": 0.9
    }
)

output_text = response["output"]["message"]["content"][0]["text"]
print(output_text)
