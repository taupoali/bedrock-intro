import boto3
import time

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def ask(model_id: str, prompt: str):
    start = time.time()
    resp = client.converse(
        modelId=model_id,
        messages=[{
            "role": "user",
            "content": [{"text": prompt}]
        }],
        inferenceConfig={"maxTokens": 300}
    )
    latency = time.time() - start

    text = resp["output"]["message"]["content"][0]["text"]
    return text, latency

prompt = "Explain the difference between Amazon S3 and Amazon EBS in simple terms."

models = [
    "amazon.nova-micro-v1:0",
    "meta.llama3-70b-instruct-v1:0",
    "mistral.mistral-large-2402-v1:0"   
]

for m in models:
    answer, t = ask(m, prompt)
    print(f"\n=== {m} ({t:.2f}s) ===\n{answer}")

