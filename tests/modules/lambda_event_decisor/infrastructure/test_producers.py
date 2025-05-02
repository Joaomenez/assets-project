import pytest
from datetime import datetime
from unittest.mock import MagicMock
from src.modules.lambda_event_decisor.domain.entities.event import Event
from src.modules.lambda_event_decisor.domain.entities.asset import Asset
from src.modules.lambda_event_decisor.domain.value_objects.event_decision import EventDecision
from src.modules.lambda_event_decisor.domain.enums.event_action import EventAction
from src.modules.lambda_event_decisor.infrastructure.producers.sqs_event_producer import SQSEventProducer

@pytest.fixture
def sqs_producer():
    """Fixture para criar um produtor SQS mockado."""
    sqs_client = MagicMock()
    sqs_client.send_message.return_value = {"MessageId": "test-message-id"}
    return SQSEventProducer(sqs_client=sqs_client)

@pytest.fixture
def sample_event():
    """Fixture para criar um evento de exemplo."""
    return Event(
        asset_id="123",
        event_type="UPSERT",
        timestamp=datetime.now().isoformat(),
        metadata={"field1": "value1"}
    )

@pytest.fixture
def sample_asset():
    """Fixture para criar um asset de exemplo."""
    return Asset(
        id="123",
        type="test",
        attributes={"field1": "value1"}
    )

@pytest.mark.asyncio
async def test_produce_event_success(sqs_producer, sample_event, sample_asset):
    """Test successful event production."""
    decision = EventDecision.upsert(sample_asset)
    result = await sqs_producer.produce_event(sample_event, decision)
    
    assert result is True
    sqs_producer.sqs_client.send_message.assert_called_once()
    
    # Verifica os argumentos da chamada
    args = sqs_producer.sqs_client.send_message.call_args
    assert args[1]["QueueUrl"] == sqs_producer.queue_url
    assert "asset_id" in args[1]["MessageBody"]

@pytest.mark.asyncio
async def test_produce_event_with_attributes(sqs_producer, sample_event, sample_asset):
    """Test event production with message attributes."""
    decision = EventDecision.upsert(sample_asset)
    attributes = {
        "EventType": {
            "DataType": "String",
            "StringValue": "UPSERT"
        }
    }
    
    result = await sqs_producer.produce_event(sample_event, decision, message_attributes=attributes)
    
    assert result is True
    sqs_producer.sqs_client.send_message.assert_called_once()
    
    # Verifica se os atributos foram passados
    args = sqs_producer.sqs_client.send_message.call_args
    assert args[1]["MessageAttributes"] == attributes

@pytest.mark.asyncio
async def test_produce_event_failure(sqs_producer, sample_event, sample_asset):
    """Test handling of production failure."""
    decision = EventDecision.upsert(sample_asset)
    # Configura o mock para simular uma falha
    sqs_producer.sqs_client.send_message.side_effect = Exception("SQS Error")
    
    with pytest.raises(Exception) as exc_info:
        await sqs_producer.produce_event(sample_event, decision)
    
    assert "SQS Error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_produce_event_with_delay(sqs_producer, sample_event, sample_asset):
    """Test event production with delay."""
    decision = EventDecision.upsert(sample_asset)
    delay_seconds = 60
    
    result = await sqs_producer.produce_event(sample_event, decision, delay_seconds=delay_seconds)
    
    assert result is True
    sqs_producer.sqs_client.send_message.assert_called_once()
    
    # Verifica se o delay foi usado
    args = sqs_producer.sqs_client.send_message.call_args
    assert args[1]["DelaySeconds"] == delay_seconds

@pytest.mark.asyncio
async def test_produce_batch_events(sqs_producer, sample_asset):
    """Test batch event production."""
    events = [
        Event(
            asset_id=f"batch-{i}",
            event_type="UPSERT",
            timestamp=datetime.now().isoformat(),
            metadata={"batch": str(i)}
        )
        for i in range(3)
    ]
    decisions = [EventDecision.upsert(sample_asset) for _ in range(3)]
    
    result = await sqs_producer.produce_batch(list(zip(events, decisions)))
    
    assert result is True
    assert sqs_producer.sqs_client.send_message.call_count == len(events)

@pytest.mark.asyncio
async def test_produce_batch_events_partial_failure(sqs_producer, sample_asset):
    """Test batch production with some failures."""
    events = [
        Event(
            asset_id=f"batch-{i}",
            event_type="UPSERT",
            timestamp=datetime.now().isoformat(),
            metadata={"batch": str(i)}
        )
        for i in range(3)
    ]
    decisions = [EventDecision.upsert(sample_asset) for _ in range(3)]
    
    # Configura o mock para falhar na segunda mensagem
    def send_with_failure(*args, **kwargs):
        if "batch-1" in args[1]["MessageBody"]:
            raise Exception("SQS Error")
        return {"MessageId": "test-message-id"}
    
    sqs_producer.sqs_client.send_message.side_effect = send_with_failure
    
    with pytest.raises(Exception) as exc_info:
        await sqs_producer.produce_batch(list(zip(events, decisions)))
    
    assert "SQS Error" in str(exc_info.value)
    assert sqs_producer.sqs_client.send_message.call_count == 2  # Deve parar na segunda mensagem 