import boto3

# -------- Configuration --------
REGION = "us-east-1"
BUCKET_NAME = "hodei-bedrock-intro"
INPUT_KEY = "input/customer_reviews.txt"
OUTPUT_KEY = "output/customer_reviews_summary.txt"

MODEL_ID = "amazon.nova-micro-v1:0"

# -------- AWS Clients --------
s3 = boto3.client("s3", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# -------- Step 1: Read input from S3 --------
response = s3.get_object(
    Bucket=BUCKET_NAME,
    Key=INPUT_KEY
)

input_text = response["Body"].read().decode("utf-8")

print("Read input from S3:")
print(input_text[:200], "...\n")  # show first 200 chars only

# -------- Step 2: Create summarization prompt --------
prompt = f"""
Instruction:
You are summarizing customer feedback for a product team.

Requirements:
- Be concise
- Highlight common themes
- Use bullet points
- Maximum of 5 bullets

Input:
{input_text}
"""

# -------- Step 3: Invoke Bedrock --------
bedrock_response = bedrock.converse(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [{"text": prompt}]
        }
    ],
    inferenceConfig={
        "maxTokens": 300,
        "temperature": 0.3,
        "topP": 0.9
    }
)

summary_text = bedrock_response["output"]["message"]["content"][0]["text"]

print("Generated summary and written to S3")
# print(summary_text, "\n")

# -------- Step 4: Write summary back to S3 --------
s3.put_object(
    Bucket=BUCKET_NAME,
    Key=OUTPUT_KEY,
    Body=summary_text.encode("utf-8"),
    ContentType="text/plain"
)

print(f"Summary written to s3://{BUCKET_NAME}/{OUTPUT_KEY}")
