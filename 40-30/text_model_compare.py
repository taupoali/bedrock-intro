import boto3
import time

# Create a Bedrock Runtime client to invoke models
client = boto3.client("bedrock-runtime", region_name="us-east-1")

def ask(model_id: str, prompt: str):
    """Send a prompt to a model and return the response text and latency."""
    
    # Record start time to measure how long the model takes to respond
    start = time.time()
    
    # Call the model using the Converse API
    resp = client.converse(
        modelId=model_id,
        messages=[{
            "role": "user",
            "content": [{"text": prompt}]
        }],
        inferenceConfig={"maxTokens": 300}
    )
    
    # Calculate how long the request took
    latency = time.time() - start

    # Extract text from the response
    # Different models return content in different formats:
    text = ""
    for block in resp["output"]["message"]["content"]:
        # Most models return regular text blocks
        if "text" in block:
            text += block["text"]
        # Reasoning models (like DeepSeek) return their thinking process
        elif "reasoningContent" in block:
            text += block["reasoningContent"]["reasoningText"]["text"]
    
    return text, latency

# The question we'll ask each model
prompt = "Explain the difference between Amazon S3 and Amazon EBS in simple terms."

# List of models to compare (using cross-region inference profiles)
models = [
    "us.meta.llama3-2-3b-instruct-v1:0",      # Small, fast model
    "us.meta.llama3-3-70b-instruct-v1:0",     # Larger, more capable model
    "us.deepseek.r1-v1:0"                     # Reasoning model (shows its thinking)
]

# Ask each model the same question and display results
for m in models:
    answer, t = ask(m, prompt)
    print(f"\n=== {m} ({t:.2f}s) ===\n{answer}")

