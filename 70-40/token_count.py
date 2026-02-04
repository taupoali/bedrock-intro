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

model_id = "amazon.nova-micro-v1:0"

prompt = "Explain Amazon S3 in one paragraph."

text, usage = ask(model_id, prompt)
print(text)
print("\nUsage:", usage)



prompts = [
    ("Plain", "Explain Amazon S3 in one sentence."),
    ("Extra punctuation", "Explain Amazon S3!!! In ONE sentence..."),
    ("Extra whitespace", "Explain   Amazon    S3   in   one   sentence."),
    ("Emoji added", "Explain Amazon S3 in one sentence 🙂📦☁️")
]


for label, p in prompts:
    _, usage = ask(model_id, p, max_tokens=60)
    print(label, "->", usage)
