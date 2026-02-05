import boto3

s3 = boto3.client("s3")

obj = s3.get_object(
    Bucket="hodei-bedrock-intro",
    Key="input/customer_reviews.txt"
)

text = obj["Body"].read().decode("utf-8")

print(text)
