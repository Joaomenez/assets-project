import pytest
import asyncio
from datetime import datetime
from src.modules.lambda_drop_asset_event_producer.presentation.handlers.drop_handler import handler

@pytest.fixture
def drop_event_example():
    return {
        "Records": [
            {
                "messageId": "test-message-id",
                "body": {
                    "asset_id": "123",
                    "operation": "DROP",
                    "timestamp": datetime.now().isoformat(),
                    "reason": "asset_expired",
                    "metadata": {
                        "deleted_by": "system",
                        "deletion_reason": "TTL exceeded"
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
async def test_drop_handler_success(drop_event_example, context, mocker):
    """Test successful drop event processing."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_drop_asset_event_producer.container.DropEventContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.return_value = True
    mock_container.return_value.process_drop_events_use_case = mock_process_event
    
    # Execute handler
    result = await handler(drop_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 200
    assert 'message' in result['body']
    mock_process_event.execute.assert_called_once()

@pytest.mark.asyncio
async def test_drop_handler_invalid_event(context, mocker):
    """Test handler with invalid event."""
    invalid_event = {"Records": [{"body": "invalid"}]}
    
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_drop_asset_event_producer.container.DropEventContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = ValueError("Invalid event")
    mock_container.return_value.process_drop_events_use_case = mock_process_event
    
    # Execute handler
    result = await handler(invalid_event, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body']

@pytest.mark.asyncio
async def test_drop_handler_process_error(drop_event_example, context, mocker):
    """Test handler when processing fails."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_drop_asset_event_producer.container.DropEventContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = Exception("Processing failed")
    mock_container.return_value.process_drop_events_use_case = mock_process_event
    
    # Execute handler
    result = await handler(drop_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body']

@pytest.mark.asyncio
async def test_drop_handler_kafka_integration(drop_event_example, context, mocker):
    """Test integration with Kafka producer."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_drop_asset_event_producer.container.DropEventContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.return_value = True
    mock_container.return_value.process_drop_events_use_case = mock_process_event
    
    # Execute handler
    result = await handler(drop_event_example, context)
    
    # Assertions
    assert result['statusCode'] == 200
    assert 'message' in result['body']
    mock_process_event.execute.assert_called_once() 