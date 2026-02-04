import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "amazon.nova-micro-v1:0"

prompt = """
Instruction:
You are an AWS instructor creating onboarding content.

Example:
Q: What is Amazon S3?
A:
- Object storage service
- Used for backups and static websites

Input:
What is Amazon EBS?

Requirements:
- Bullet points
- Max 3 bullets

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
        "maxTokens": 200,
        "temperature": 0.3,
        "topP": 0.9
    }
)

output_text = response["output"]["message"]["content"][0]["text"]
print(output_text)
