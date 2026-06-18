import os
from config import Config


def is_aws_configured():
    """Check if AWS credentials and bucket are configured."""
    return bool(
        Config.AWS_ACCESS_KEY_ID
        and Config.AWS_SECRET_ACCESS_KEY
        and Config.S3_BUCKET
        and Config.USE_AWS
    )


class S3Service:
    def __init__(self):
        if not is_aws_configured():
            raise ValueError(
                'AWS is not configured. Set USE_AWS=true and AWS credentials in .env'
            )

        import boto3
        self.bucket = Config.S3_BUCKET
        self.client = boto3.client(
            's3',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )

    def upload_file(self, local_path, s3_key):
        """Upload a local file to S3."""
        self.client.upload_file(local_path, self.bucket, s3_key)
        return self.get_uri(s3_key)

    def download_file(self, s3_key, local_path):
        """Download a file from S3."""
        os.makedirs(os.path.dirname(local_path) or '.', exist_ok=True)
        self.client.download_file(self.bucket, s3_key, local_path)
        return local_path

    def upload_bytes(self, data, s3_key, content_type='application/octet-stream'):
        """Upload raw bytes to S3."""
        self.client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=data,
            ContentType=content_type,
        )
        return self.get_uri(s3_key)

    def get_uri(self, s3_key):
        return f's3://{self.bucket}/{s3_key}'

    def key_from_uri(self, s3_uri):
        if s3_uri.startswith('s3://'):
            return s3_uri.replace(f's3://{self.bucket}/', '')
        return s3_uri

    def list_objects(self, prefix):
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]

    def object_exists(self, s3_key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except self.client.exceptions.ClientError:
            return False
