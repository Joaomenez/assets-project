import pytest
import asyncio
from datetime import datetime
from src.modules.lambda_redrive.presentation.handlers.redrive_handler import handler

@pytest.fixture
def redrive_event_example():
    return {
        "Records": [
            {
                "messageId": "test-message-id",
                "body": {
                    "original_message_id": "original-123",
                    "original_queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/original-queue",
                    "failure_reason": "processing_error",
                    "retry_count": 1,
                    "original_payload": {
                        "asset_id": "123",
                        "operation": "UPSERT",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        ]
    }

@pytest.fixture
def context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "test-function"
            self.function_version = "1"
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
            self.memory_limit_in_mb = 128
            self.aws_request_id = "test-request-id"
            self.log_group_name = "test-log-group"
            self.log_stream_name = "test-log-stream"

    return LambdaContext()

@pytest.mark.asyncio
async def test_redrive_handler_success(redrive_event_example, context, mocker):
    """Test successful redrive event processing."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_redrive.container.RedriveContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.return_value = {'messages': [{'id': '1'}]}
    mock_container.return_value.process_dlq_events_use_case = mock_process_event
    mock_container.return_value.get_default_dlq_urls.return_value = ['dlq-url']
    
    # Execute handler
    result = await handler(redrive_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 200
    assert 'message' in result['body']
    mock_process_event.execute.assert_called_once()

@pytest.mark.asyncio
async def test_redrive_handler_invalid_event(context, mocker):
    """Test handler with invalid event."""
    invalid_event = {"Records": [{"body": "invalid"}]}
    
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_redrive.container.RedriveContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = ValueError("Invalid event")
    mock_container.return_value.process_dlq_events_use_case = mock_process_event
    mock_container.return_value.get_default_dlq_urls.return_value = ['dlq-url']
    
    # Execute handler
    result = await handler(invalid_event, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body']

@pytest.mark.asyncio
async def test_redrive_handler_process_error(redrive_event_example, context, mocker):
    """Test handler when processing fails."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_redrive.container.RedriveContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = Exception("Processing failed")
    mock_container.return_value.process_dlq_events_use_case = mock_process_event
    mock_container.return_value.get_default_dlq_urls.return_value = ['dlq-url']
    
    # Execute handler
    result = await handler(redrive_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body']

@pytest.mark.asyncio
async def test_redrive_handler_max_retries(redrive_event_example, context, mocker):
    """Test handler when max retries is reached."""
    # Modify event to simulate max retries
    redrive_event_example["Records"][0]["body"]["retry_count"] = 5
    
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_redrive.container.RedriveContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = ValueError("Max retries exceeded")
    mock_container.return_value.process_dlq_events_use_case = mock_process_event
    mock_container.return_value.get_default_dlq_urls.return_value = ['dlq-url']
    
    # Execute handler
    result = await handler(redrive_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body']

@pytest.mark.asyncio
async def test_redrive_handler_sqs_integration(redrive_event_example, context, mocker):
    """Test integration with SQS."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_redrive.container.RedriveContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.return_value = {'messages': [{'id': '1', 'status': 'redriven'}]}
    mock_container.return_value.process_dlq_events_use_case = mock_process_event
    mock_container.return_value.get_default_dlq_urls.return_value = ['dlq-url']
    
    # Execute handler
    result = await handler(redrive_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 200
    assert 'message' in result['body']
    assert result['body']['results']['total_processed'] == 1
    mock_process_event.execute.assert_called_once() 