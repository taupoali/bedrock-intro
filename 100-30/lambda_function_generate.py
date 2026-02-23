import boto3
import urllib.parse

# --- Configuration ---
REGION = "us-east-1"
MODEL_ID = "us.meta.llama3-2-3b-instruct-v1:0"

s3 = boto3.client("s3", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def lambda_handler(event, context):
    # 1) Get bucket + key from the S3 event
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    # Optional safety: only process files under input/
    if not key.startswith("input/"):
        print(f"Skipping object (not under input/): s3://{bucket}/{key}")
        return {"skipped": True, "reason": "not_input_prefix", "bucket": bucket, "key": key}

    # 2) Read input from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    input_text = obj["Body"].read().decode("utf-8")

    print(f"Read {len(input_text)} characters from s3://{bucket}/{key}")

    # 3) Create summarization prompt (same pattern as Lab A)
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
""".strip()

    # 4) Invoke Bedrock (same invocation pattern)
    br_resp = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.3,
            "topP": 0.9
        }
    )

    summary_text = br_resp["output"]["message"]["content"][0]["text"]
    print("Generated summary length:", len(summary_text))

    # 5) Write output back to S3 under output/
    filename = key.split("/")[-1]  # e.g. customer_reviews.txt
    base = filename.rsplit(".", 1)[0]  # customer_reviews
    output_key = f"output/{base}_summary.txt"

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=summary_text.encode("utf-8"),
        ContentType="text/plain"
    )

    print(f"Wrote summary to s3://{bucket}/{output_key}")

    return {
        "bucket": bucket,
        "input_key": key,
        "output_key": output_key
    }
