import boto3

bedrock = boto3.client("bedrock", region_name="eu-west-1")

response = bedrock.list_foundation_models()

for model in response["modelSummaries"]:
    if "TEXT" in model["inputModalities"]:
        print(f"{model['modelId']} - {model['providerName']}")
