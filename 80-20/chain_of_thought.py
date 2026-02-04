import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "amazon.nova-micro-v1:0"

prompt = """
You are an AWS instructor.

Problem:
An EC2 instance costs $0.10 per hour. How much does it cost to run for 3 days?

Show your working step by step before giving the final answer.
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
