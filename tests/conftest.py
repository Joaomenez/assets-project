import pytest
from moto import mock_dynamodb, mock_sqs, mock_sns

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="function")
def dynamodb(aws_credentials):
    """DynamoDB mock fixture."""
    with mock_dynamodb():
        yield

@pytest.fixture(scope="function")
def sqs(aws_credentials):
    """SQS mock fixture."""
    with mock_sqs():
        yield

@pytest.fixture(scope="function")
def sns(aws_credentials):
    """SNS mock fixture."""
    with mock_sns():
        yield 