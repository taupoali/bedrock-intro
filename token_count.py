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


pairs = [
    ("Plain English", "Explain Amazon S3 in one sentence."),
    ("Lots of punctuation", "Explain Amazon S3!!! In ONE sentence... (seriously)"),
    ("Emoji + symbols", "Explain Amazon S3 in one sentence 🙂📦☁️ #storage"),
    ("Long compound word", "Explain antidisestablishmentarianism in one sentence.")
]

for label, p in pairs:
    _, usage = ask(model_id, p, max_tokens=60)
    print(label, "->", usage)
