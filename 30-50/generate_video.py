import json
import time
import boto3

REGION = "us-east-1"
PROFILE = "bedrock_dev"
MODEL_ID = "amazon.nova-reel-v1:1"

# S3 location where the video will be written
S3_OUTPUT_URI = "s3://bedrock-video-generation-us-east-1-sejocm"

# 1) Create a boto3 session using the named AWS CLI profile
session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

# 2) Create the Bedrock Runtime client from that session
bedrock_runtime = session.client("bedrock-runtime")

# 3) Define the video generation request
model_input = {
    "taskType": "TEXT_VIDEO",
    "textToVideoParams": {
        "text": "Japanese style cartoon of a masked martial arts expert jumping from one roof to another at night."
    },
    "videoGenerationConfig": {
        "durationSeconds": 6,
        "fps": 24,
        "dimension": "1280x720",
        "seed": 0
    }
}

# 4) Start the async video generation job
start_response = bedrock_runtime.start_async_invoke(
    modelId=MODEL_ID,
    modelInput=model_input,
    outputDataConfig={
        "s3OutputDataConfig": {
            "s3Uri": S3_OUTPUT_URI
        }
    }
)

invocation_arn = start_response["invocationArn"]
print("Started video generation job:")
print(invocation_arn)

# 5) Poll the job status until it completes
while True:
    status_response = bedrock_runtime.get_async_invoke(
        invocationArn=invocation_arn
    )

    status = status_response["status"]
    print("Current status:", status)

    if status in ("Completed", "Failed", "Stopped"):
        break

    time.sleep(10)

# 6) Show final result
print("\nFinal status:", status)
print(json.dumps(status_response, indent=2, default=str))

if status == "Completed":
    print("\nVideo successfully generated.")
    print("Check the output location in S3:")
    print(S3_OUTPUT_URI)
else:
    print("\nVideo generation did not complete successfully.")
