import boto3

REGION = "us-east-1"
MODEL_ID = "us.meta.llama3-3-70b-instruct-v1:0"  # If your catalog shows a different ID, use that.

brt = boto3.client("bedrock-runtime", region_name=REGION)

prompt = "Explain what Amazon Bedrock is in 2 short bullet points."

response = brt.converse(
    modelId=MODEL_ID,
    messages=[
        {"role": "user", 
         "content": [{"text": prompt}]
        }
    ],
    inferenceConfig={
        "maxTokens": 200, 
        "temperature": 0.5}
)

print(response["output"]["message"]["content"][0]["text"])
