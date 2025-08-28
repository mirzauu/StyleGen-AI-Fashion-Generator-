from typing import Any
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from fastapi import UploadFile
import tempfile

class StorageService:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

    def upload_file(self, file_path: str, object_name: str) -> bool:
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            return True
        except FileNotFoundError:
            print(f"The file was not found: {file_path}")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except ClientError as e:
            print(f"Failed to upload file: {e}")
            return False

    def download_file(self, object_name: str, file_path: str) -> bool:
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            print(f"Failed to download file: {e}")
            return False

    def list_files(self, prefix: str = '') -> list:
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            print(f"Failed to list files: {e}")
            return []

    def delete_file(self, object_name: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Failed to delete file: {e}")
            return False

async def upload_file_to_storage(upload_file: UploadFile, object_name: str = None) -> str:
    """
    Uploads an UploadFile to S3 and returns the file URL.
    """
    storage_service = StorageService(bucket_name=os.getenv("S3_BUCKET", "your-bucket-name"))
    suffix = os.path.splitext(upload_file.filename)[-1]
    object_name = object_name or f"uploads/{next(tempfile._get_candidate_names())}{suffix}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        tmp.flush()
        storage_service.upload_file(tmp.name, object_name)
    # Construct the S3 URL (adjust as needed for your setup)
    s3_url = f"https://{storage_service.bucket_name}.s3.amazonaws.com/{object_name}"
    return s3_url

# Usage example (to be removed or commented out in production):
# storage_service = StorageService(bucket_name='your-bucket-name')
# storage_service.upload_file('path/to/local/file.jpg', 'models/1/pose_label.jpg')