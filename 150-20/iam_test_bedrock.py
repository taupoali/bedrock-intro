import boto3
import os
from botocore.exceptions import ClientError

REGION = "us-east-1"

def try_converse(model_id: str):
    client = boto3.client("bedrock-runtime", region_name=REGION)
    try:
        resp = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Say hello in one sentence."}]}],
            inferenceConfig={"maxTokens": 50, "temperature": 0.2},
        )
        text = "\n".join(p.get("text","") for p in resp["output"]["message"].get("content", [])).strip()
        print(f"\nSUCCESS for model: {model_id}\n{text}\n")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        print(f"\nDENIED for model: {model_id}\n{code} - {msg}\n")

if __name__ == "__main__":
    allowed_model = "amazon.nova-micro-v1:0"
    denied_model = os.environ.get("DENIED_MODEL_ID", "amazon.nova-lite-v1:0")  # change if needed

    try_converse(allowed_model)
    try_converse(denied_model)
