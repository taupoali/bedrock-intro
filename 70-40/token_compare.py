import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def ask(model_id: str, prompt: str, max_tokens: int = 200):
    resp = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens}
    )

    text = resp["output"]["message"]["content"][0]["text"]
    usage = resp.get("usage", {})
    stop_reason = resp.get("stopReason", "unknown")
    
    return text, usage, stop_reason

model_id = "us.meta.llama3-1-8b-instruct-v1:0"

prompt = "Explain Amazon S3 in one paragraph."

# Test how different maxTokens limits affect the response
print("=== Impact of maxTokens Limit ===")
print("Testing the same prompt with different token limits...\n")

token_limits = [10, 25, 50, 100, 200]

for limit in token_limits:
    text, usage, stop_reason = ask(model_id, prompt, max_tokens=limit)
    
    print(f"--- maxTokens: {limit} ---")
    print(f"Generated text: {text}")
    print(f"Output tokens: {usage.get('outputTokens', 0)}")
    print(f"Stop reason: {stop_reason}")
    print()
