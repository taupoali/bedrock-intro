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

model_id = "us.meta.llama3-1-8b-instruct-v1:0"
base_prompt = "Summarize the following text in 10 bullet points:\n\n"

paragraph = (
    "Amazon S3 is an object storage service designed to store and retrieve "
    "any amount of data from anywhere. It is commonly used for backups, "
    "static website hosting, data lakes, and archival storage.\n\n"
)

short_input = base_prompt + paragraph
long_input = base_prompt + paragraph + paragraph + paragraph + paragraph

MAX_TOKENS = 120
_, short_usage = ask(model_id, short_input, max_tokens=MAX_TOKENS)
_, long_usage  = ask(model_id, long_input,  max_tokens=MAX_TOKENS)

print("Short input:", short_usage)
print("Long input :", long_usage)

