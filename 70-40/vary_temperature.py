import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def ask_temp(model_id: str, prompt: str, temp: float):
    resp = client.converse(
        modelId=model_id,
        messages=[{"role":"user","content":[{"text":prompt}]}],
        inferenceConfig={"maxTokens": 120, "temperature": temp}
    )
    return resp["output"]["message"]["content"][0]["text"]

model_id = "us.meta.llama3-2-3b-instruct-v1:0"
prompt = "Give me 5 creative names for a cloud storage training course."

for t in [0.0, 0.3, 0.9]:
    print(f"\n--- temperature={t} ---")
    print(ask_temp(model_id, prompt, t))
