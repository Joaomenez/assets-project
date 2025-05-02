import pytest
from datetime import datetime
from src.modules.lambda_event_decisor.domain.entities.event import Event
from src.modules.lambda_event_decisor.domain.entities.asset import Asset
from src.modules.lambda_event_decisor.domain.value_objects.event_decision import EventDecision
from src.modules.lambda_event_decisor.domain.enums.event_action import EventAction

def test_event_creation():
    """Test event entity creation."""
    event_data = {
        "asset_id": "123",
        "event_type": "UPSERT",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"field1": "value1"}
    }
    
    event = Event(**event_data)
    
    assert event.asset_id == event_data["asset_id"]
    assert event.event_type == event_data["event_type"]
    assert event.metadata == event_data["metadata"]

def test_event_validation():
    """Test event validation."""
    with pytest.raises(ValueError):
        Event(
            asset_id="",  # ID vazio deve falhar
            event_type="INVALID_TYPE",  # Tipo inválido deve falhar
            timestamp=datetime.now().isoformat(),
            metadata={}
        )

def test_event_decision_creation():
    """Test event decision creation."""
    asset = Asset(id="123", type="test", attributes={"field1": "value1"})
    decision = EventDecision.upsert(asset)
    
    assert decision.action == EventAction.UPSERT
    assert decision.asset == asset
    assert decision.should_produce_event() is True

def test_event_decision_drop():
    """Test event decision drop."""
    asset = Asset(id="123", type="test", attributes={"field1": "value1"})
    decision = EventDecision.drop(asset)
    
    assert decision.action == EventAction.DROP
    assert decision.asset == asset
    assert decision.should_produce_event() is True

def test_event_decision_no_action():
    """Test event decision no action."""
    asset = Asset(id="123", type="test", attributes={"field1": "value1"})
    decision = EventDecision.no_action(asset)
    
    assert decision.action == EventAction.NO_ACTION
    assert decision.asset == asset
    assert decision.should_produce_event() is False

def test_event_to_dict():
    """Test event serialization."""
    timestamp = datetime.now().isoformat()
    event_data = {
        "asset_id": "123",
        "event_type": "UPSERT",
        "timestamp": timestamp,
        "metadata": {"field1": "value1"}
    }
    
    event = Event(**event_data)
    event_dict = event.to_dict()
    
    assert event_dict["asset_id"] == event_data["asset_id"]
    assert event_dict["event_type"] == event_data["event_type"]
    assert event_dict["timestamp"] == timestamp
    assert event_dict["metadata"] == event_data["metadata"] 