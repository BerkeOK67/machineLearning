import json
import os
import time
from datetime import datetime

from config import Config
from cloud.aws_s3 import is_aws_configured


class SageMakerTrainer:
    def __init__(self):
        if not is_aws_configured():
            raise ValueError('AWS is not configured')

        if not Config.AWS_SAGEMAKER_ROLE:
            raise ValueError('AWS_SAGEMAKER_ROLE is required for SageMaker training')

        import boto3
        import sagemaker
        from sagemaker.sklearn import SKLearn

        self.session = sagemaker.Session(
            boto_session=boto3.Session(
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            )
        )
        self.role = Config.AWS_SAGEMAKER_ROLE
        self.instance_type = Config.SAGEMAKER_INSTANCE_TYPE
        self.sklearn_cls = SKLearn
        self.sagemaker_client = boto3.client(
            'sagemaker',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )

    def start_training_job(
        self,
        dataset_s3_uri,
        target_column,
        algorithm='RandomForest',
        model_type='classification',
        job_name=None,
    ):
        if not job_name:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            job_name = f'ml-platform-{algorithm.lower()}-{timestamp}'[:63]

        script_dir = os.path.join(os.path.dirname(__file__), 'sagemaker')

        estimator = self.sklearn_cls(
            entry_point='train.py',
            source_dir=script_dir,
            role=self.role,
            instance_count=1,
            instance_type=self.instance_type,
            framework_version=Config.SAGEMAKER_FRAMEWORK_VERSION,
            py_version='py3',
            sagemaker_session=self.session,
            hyperparameters={
                'target-column': target_column,
                'algorithm': algorithm,
                'model-type': model_type,
            },
            output_path=f's3://{Config.S3_BUCKET}/models/output',
            base_job_name='ml-platform-train',
        )

        estimator.fit({'train': dataset_s3_uri}, job_name=job_name, wait=False)

        return {
            'job_name': job_name,
            'status': 'InProgress',
            'dataset_s3_uri': dataset_s3_uri,
        }

    def get_job_status(self, job_name):
        response = self.sagemaker_client.describe_training_job(TrainingJobName=job_name)
        status = response['TrainingJobStatus']

        result = {
            'job_name': job_name,
            'status': status,
            'created_at': response.get('CreationTime', '').isoformat() if response.get('CreationTime') else None,
            'ended_at': response.get('TrainingEndTime', '').isoformat() if response.get('TrainingEndTime') else None,
            'failure_reason': response.get('FailureReason'),
            'model_artifacts': response.get('ModelArtifacts', {}).get('S3ModelArtifacts'),
        }

        if status == 'Completed':
            result['metrics'] = self._load_metrics_from_output(response)

        return result

    def _load_metrics_from_output(self, job_response):
        model_tar = job_response.get('ModelArtifacts', {}).get('S3ModelArtifacts')
        if not model_tar:
            return {}

        # Metrics are printed in CloudWatch logs; for MVP return placeholder from job name
        return {'note': 'Check SageMaker console or CloudWatch for detailed metrics'}

    def wait_for_job(self, job_name, poll_interval=30, timeout=3600):
        start = time.time()
        while time.time() - start < timeout:
            status_info = self.get_job_status(job_name)
            if status_info['status'] in {'Completed', 'Failed', 'Stopped'}:
                return status_info
            time.sleep(poll_interval)
        raise TimeoutError(f'Training job {job_name} timed out')
