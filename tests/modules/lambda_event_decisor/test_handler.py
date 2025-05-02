import pytest
import asyncio
from datetime import datetime
from src.modules.lambda_event_decisor.presentation.handlers.event_decisor_handler import handler

@pytest.fixture
def event_example():
    return {
        "Records": [
            {
                "messageId": "test-message-id",
                "body": {
                    "asset_id": "123",
                    "event_type": "UPSERT",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "field1": "value1",
                        "field2": "value2"
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
async def test_handler_success(event_example, context, mocker):
    """Test successful event processing."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_event_decisor.container.EventDecisionContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.return_value = True
    mock_container.return_value.process_event_use_case = mock_process_event
    
    # Execute handler
    result = await handler(event_example, context)
    
    # Assertions
    assert result['statusCode'] == 200
    assert 'message' in result['body']
    mock_process_event.execute.assert_called_once()

@pytest.mark.asyncio
async def test_handler_invalid_event(context, mocker):
    """Test handler with invalid event."""
    invalid_event = {"Records": [{"body": "invalid"}]}
    
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_event_decisor.container.EventDecisionContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = ValueError("Invalid event")
    mock_container.return_value.process_event_use_case = mock_process_event
    
    # Execute handler
    result = await handler(invalid_event, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body']

@pytest.mark.asyncio
async def test_handler_process_error(event_example, context, mocker):
    """Test handler when processing fails."""
    # Mock dependencies
    mock_container = mocker.patch('src.modules.lambda_event_decisor.container.EventDecisionContainer')
    mock_process_event = mocker.AsyncMock()
    mock_process_event.execute.side_effect = Exception("Processing failed")
    mock_container.return_value.process_event_use_case = mock_process_event
    
    # Execute handler
    result = await handler(event_example, context)
    
    # Assertions
    assert result['statusCode'] == 500
    assert 'error' in result['body'] 