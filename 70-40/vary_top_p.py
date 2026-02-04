import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "amazon.nova-micro-v1:0"

def ask_top_p(prompt: str, temperature: float, top_p: float):
    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 120,
            "temperature": temperature,
            "topP": top_p
        }
    )
    return response["output"]["message"]["content"][0]["text"]

prompt = "Give me 5 creative names for a cloud storage training course."

TEMPERATURE = 0.7  # keep this constant

for top_p in [0.3, 0.6, 0.9]:
    print(f"\n--- top_p = {top_p} ---")
    print(ask_top_p(prompt, TEMPERATURE, top_p))
