import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def ask(model_id: str, prompt: str, max_tokens: int = 200):
    resp = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens}
    )

    text = resp["output"]["message"]["content"][0]["text"]

    # Usage is commonly present; if it isn't, print(resp.keys()) to inspect.
    usage = resp.get("usage", {})
    return text, usage

#model_id = "us.meta.llama3-2-3b-instruct-v1:0"
model_id = "us.meta.llama3-1-8b-instruct-v1:0"

prompt = "Explain Amazon S3 in one paragraph."

# First, let's see a complete example with both output and token usage
print("=== Example: Full Response ===")
text, usage = ask(model_id, prompt)
print(f"Generated text:\n{text}")
print(f"\nToken usage: {usage}")


# Now let's compare how different prompt variations affect token counts
print("\n\n=== Token Count Comparison ===")
print("Testing how prompt formatting affects input token counts...\n")

prompts = [
    ("Plain", "Explain Amazon S3 in one sentence."),
    ("Extra punctuation", "Explain Amazon S3!!! In ONE sentence..."),
    ("Extra whitespace", "Explain   Amazon    S3   in   one   sentence."),
    ("Emoji added", "Explain Amazon S3 in one sentence 🙂📦☁️")
]

for label, p in prompts:
    _, usage = ask(model_id, p, max_tokens=300)
    print(f"{label:20} -> Input: {usage.get('inputTokens', 0):3} tokens, Output: {usage.get('outputTokens', 0):3} tokens")
