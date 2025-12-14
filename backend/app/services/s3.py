import boto3
import uuid

s3 = boto3.client("s3")
BUCKET = "your-bucket"

def upload_file(local_path: str) -> str:
    key = f"media/{uuid.uuid4()}"
    s3.upload_file(local_path, BUCKET, key)
    return f"s3://{BUCKET}/{key}"
