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

model_id = "us.meta.llama3-2-3b-instruct-v1:0"
base_prompt = "Summarize the following text in 10 bullet points:\n\n"

paragraph = (
    "Amazon S3 is an object storage service designed to store and retrieve "
    "any amount of data from anywhere. It is commonly used for backups, "
    "static website hosting, data lakes, and archival storage.\n\n"
)

# Create two different sized inputs to compare token usage
short_input = base_prompt + paragraph                    # 1 paragraph
long_input = base_prompt + paragraph * 4                 # 4 paragraphs (same text repeated)

print("=== Context Window Comparison ===")
print("Testing how input size affects token usage...\n")

MAX_TOKENS = 120

print(f"Short input: {len(short_input)} characters (1 paragraph)")
_, short_usage = ask(model_id, short_input, max_tokens=MAX_TOKENS)
print(f"Token usage: {short_usage}\n")

print(f"Long input: {len(long_input)} characters (4 paragraphs)")
_, long_usage = ask(model_id, long_input, max_tokens=MAX_TOKENS)
print(f"Token usage: {long_usage}\n")

print("--- Key Insight ---")
print(f"Input tokens increased from {short_usage.get('inputTokens', 0)} to {long_usage.get('inputTokens', 0)}")
print(f"Output tokens stayed similar: {short_usage.get('outputTokens', 0)} vs {long_usage.get('outputTokens', 0)}")
print("Larger context = more input tokens = higher cost!")

