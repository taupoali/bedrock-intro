import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "us.meta.llama3-2-3b-instruct-v1:0"  # use the same model throughout the lab

prompt = """
Instruction: You are an AWS instructor explaining concepts to beginners.
Content: The learner is new to cloud computing and has no AWS experience
Prompt: Explain Amazon S3"
"""

response = client.converse(
    modelId=model_id,
    messages=[
        {
            "role": "user",
            "content": [
                {"text": prompt}
            ]
        }
    ],
    inferenceConfig={
        "maxTokens": 300
    }
)

output_text = response["output"]["message"]["content"][0]["text"]

print(output_text)
