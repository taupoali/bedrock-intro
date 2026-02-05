import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "amazon.nova-micro-v1:0"

prompt = """
Instruction:
You are an IT journalist.

Input:
Does RunITAnywhere SaaS product support Azure?
Cite a source for your information.
If you don't know the answer say so in a single sentence.
If you don't know the answer, do not make up an answer.
If you don't know the answer, do not give me recommendations on where to find out.
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
