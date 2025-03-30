import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Cloudflare R2 Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = '12c0afa42dbcbd1f1105923a0bfa83fb'
AWS_SECRET_ACCESS_KEY = '0c184bc9dcd72a23ff3b441e5593c9628248e59bdb1d3ff0c85a4164ecb83a1b'
AWS_STORAGE_BUCKET_NAME = 'brymax-uploads'
AWS_S3_ENDPOINT_URL = 'https://b02658842e315caa9e0a14f4e8e5e169.r2.cloudflarestorage.com'

# Local uploads folder
LOCAL_FOLDER = r"D:\BRYMAX\BRYMAX OFFICIAL DATA MANAGEMENT SYSTEM2\app\uploads"  # Ensure this matches the exact folder path


def upload_to_s3(local_folder, bucket_name, endpoint_url, access_key, secret_key):
    """
    Upload all files from the local folder to the specified S3 bucket.
    """
    try:
        # Initialize the S3 client
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        # Iterate through all files in the local folder
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_path = os.path.join(root, file)
                # Define the S3 key, preserving the folder structure
                s3_key = os.path.relpath(local_path, local_folder).replace("\\", "/")

                try:
                    # Upload file to S3
                    print(f"Uploading '{file}' to S3 bucket '{bucket_name}'...")
                    s3.upload_file(local_path, bucket_name, s3_key)
                    print(f"'{file}' uploaded successfully.")
                except ClientError as e:
                    print(f"Failed to upload '{file}': {str(e)}")
    except NoCredentialsError:
        print("Error: AWS credentials are missing. Please check your configuration.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    # Trigger the upload process
    upload_to_s3(LOCAL_FOLDER, AWS_STORAGE_BUCKET_NAME, AWS_S3_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
