import json
from datetime import datetime

from config import Config
from cloud.aws_s3 import is_aws_configured


class SageMakerDeployer:
    def __init__(self):
        if not is_aws_configured():
            raise ValueError('AWS is not configured')

        if not Config.AWS_SAGEMAKER_ROLE:
            raise ValueError('AWS_SAGEMAKER_ROLE is required for SageMaker deployment')

        import boto3
        import sagemaker
        from sagemaker.sklearn.model import SKLearnModel

        self.session = sagemaker.Session(
            boto_session=boto3.Session(
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            )
        )
        self.role = Config.AWS_SAGEMAKER_ROLE
        self.instance_type = Config.SAGEMAKER_ENDPOINT_INSTANCE_TYPE
        self.sklearn_model_cls = SKLearnModel
        self.runtime_client = boto3.client(
            'sagemaker-runtime',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )
        self.sagemaker_client = boto3.client(
            'sagemaker',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )

    def deploy_model(self, model_artifacts_s3_uri, endpoint_name=None):
        if not endpoint_name:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            endpoint_name = f'ml-platform-endpoint-{timestamp}'[:63]

        model = self.sklearn_model_cls(
            model_data=model_artifacts_s3_uri,
            role=self.role,
            entry_point='inference.py',
            source_dir=self._inference_source_dir(),
            framework_version=Config.SAGEMAKER_FRAMEWORK_VERSION,
            py_version='py3',
            sagemaker_session=self.session,
        )

        # wait=False → Flask bloke olmaz, endpoint arka planda oluşur
        model.deploy(
            initial_instance_count=1,
            instance_type=self.instance_type,
            endpoint_name=endpoint_name,
            wait=False,
        )

        return {
            'endpoint_name': endpoint_name,
            'status': 'Creating',
            'model_artifacts': model_artifacts_s3_uri,
        }

    def predict(self, endpoint_name, input_data):
        payload = json.dumps({'instances': [input_data]})
        response = self.runtime_client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=payload,
        )
        body = response['Body'].read().decode('utf-8')
        return json.loads(body)

    def get_endpoint_status(self, endpoint_name):
        response = self.sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        return {
            'endpoint_name': endpoint_name,
            'status': response['EndpointStatus'],
            'created_at': response.get('CreationTime', '').isoformat() if response.get('CreationTime') else None,
        }

    def delete_endpoint(self, endpoint_name):
        self.sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        return {'message': f'Endpoint {endpoint_name} deletion started'}

    def _inference_source_dir(self):
        import os
        return os.path.join(os.path.dirname(__file__), 'sagemaker')
