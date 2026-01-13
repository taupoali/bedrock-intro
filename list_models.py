import boto3

REGION = "us-east-1"

bedrock = boto3.client("bedrock", region_name=REGION)

response = bedrock.list_foundation_models()

print(f"Found {len(response['modelSummaries'])} models\n")

for m in response["modelSummaries"]:
    # A few useful fields to show beginners
    print(f"- {m.get('modelName')}  |  modelId={m.get('modelId')}")
