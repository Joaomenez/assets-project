import pytest
from datetime import datetime
from src.modules.lambda_event_decisor.domain.entities.event import Event
from src.modules.lambda_event_decisor.domain.entities.asset import Asset
from src.modules.lambda_event_decisor.domain.value_objects.event_decision import EventDecision
from src.modules.lambda_event_decisor.domain.enums.event_action import EventAction
from src.modules.lambda_event_decisor.application.use_cases.process_event import ProcessEvent
from src.modules.lambda_event_decisor.domain.services.event_decision_service import EventDecisionService

@pytest.fixture
def event_service():
    return EventDecisionService()

@pytest.fixture
def process_event_use_case(event_service, mocker):
    mock_producer = mocker.AsyncMock()
    mock_producer.produce_event.return_value = True
    
    mock_storage = mocker.AsyncMock()
    mock_storage.store_event.return_value = True
    
    mock_repository = mocker.AsyncMock()
    mock_repository.save.return_value = True
    
    return ProcessEvent(
        event_service=event_service,
        event_producer=mock_producer,
        event_storage=mock_storage,
        asset_repository=mock_repository
    )

@pytest.fixture
def valid_event():
    return Event(
        asset_id="123",
        event_type="UPSERT",
        timestamp=datetime.now().isoformat(),
        metadata={"field1": "value1"}
    )

@pytest.fixture
def valid_asset():
    return Asset(
        id="123",
        type="test",
        attributes={"field1": "value1"}
    )

@pytest.mark.asyncio
async def test_process_valid_event(process_event_use_case, valid_event, valid_asset):
    """Test processing of valid event."""
    result = await process_event_use_case.execute(valid_event)
    
    assert result is True
    process_event_use_case.event_producer.produce_event.assert_called_once()
    process_event_use_case.event_storage.store_event.assert_called_once()
    process_event_use_case.asset_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_invalid_event(process_event_use_case):
    """Test processing of invalid event."""
    invalid_event = Event(
        asset_id="123",
        event_type="INVALID",
        timestamp=datetime.now().isoformat(),
        metadata={}
    )
    
    result = await process_event_use_case.execute(invalid_event)
    
    assert result is False
    process_event_use_case.event_producer.produce_event.assert_not_called()
    process_event_use_case.event_storage.store_event.assert_not_called()
    process_event_use_case.asset_repository.save.assert_not_called()

@pytest.mark.asyncio
async def test_process_event_producer_error(process_event_use_case, valid_event, valid_asset):
    """Test handling of producer error."""
    process_event_use_case.event_producer.produce_event.side_effect = Exception("Producer Error")
    
    with pytest.raises(Exception) as exc_info:
        await process_event_use_case.execute(valid_event)
    
    assert "Producer Error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_process_event_with_retry(process_event_use_case, valid_event, valid_asset, mocker):
    """Test event processing with retry logic."""
    # Configura o mock para falhar na primeira tentativa e suceder na segunda
    process_event_use_case.event_producer.produce_event.side_effect = [
        Exception("First attempt fails"),
        True
    ]
    
    result = await process_event_use_case.execute(valid_event)
    
    assert result is True
    assert process_event_use_case.event_producer.produce_event.call_count == 2

@pytest.mark.asyncio
async def test_process_expired_event(process_event_use_case):
    """Test processing of expired event."""
    expired_event = Event(
        asset_id="123",
        event_type="UPSERT",
        timestamp="2020-01-01T00:00:00",
        metadata={"field1": "value1"}
    )
    
    result = await process_event_use_case.execute(expired_event)
    
    assert result is False
    process_event_use_case.event_producer.produce_event.assert_not_called()
    process_event_use_case.event_storage.store_event.assert_not_called()
    process_event_use_case.asset_repository.save.assert_not_called()

@pytest.mark.asyncio
async def test_process_duplicate_event(process_event_use_case, valid_event, valid_asset):
    """Test processing of duplicate event."""
    # Primeira execução deve ser bem-sucedida
    first_result = await process_event_use_case.execute(valid_event)
    assert first_result is True
    
    # Reset dos mocks para limpar o histórico de chamadas
    process_event_use_case.event_producer.produce_event.reset_mock()
    process_event_use_case.event_storage.store_event.reset_mock()
    process_event_use_case.asset_repository.save.reset_mock()
    
    # Segunda execução com o mesmo evento deve ser ignorada
    second_result = await process_event_use_case.execute(valid_event)
    assert second_result is False
    process_event_use_case.event_producer.produce_event.assert_not_called()
    process_event_use_case.event_storage.store_event.assert_not_called()
    process_event_use_case.asset_repository.save.assert_not_called() 