import pytest
from datetime import datetime
from src.modules.lambda_event_decisor.domain.entities.event import Event
from src.modules.lambda_event_decisor.domain.entities.asset import Asset
from src.modules.lambda_event_decisor.domain.value_objects.event_decision import EventDecision
from src.modules.lambda_event_decisor.domain.enums.event_action import EventAction
from src.modules.lambda_event_decisor.domain.services.event_decision_service import EventDecisionService

@pytest.fixture
def event_service():
    return EventDecisionService()

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

def test_decide_upsert_event(event_service, valid_event, valid_asset):
    """Test decision for upsert event."""
    decision = event_service.decide(valid_event, valid_asset)
    
    assert isinstance(decision, EventDecision)
    assert decision.action == EventAction.UPSERT
    assert decision.asset == valid_asset
    assert decision.should_produce_event() is True
    assert decision.should_save_asset() is True

def test_decide_drop_event(event_service, valid_asset):
    """Test decision for drop event."""
    drop_event = Event(
        asset_id="123",
        event_type="DROP",
        timestamp=datetime.now().isoformat(),
        metadata={"reason": "expired"}
    )
    
    decision = event_service.decide(drop_event, valid_asset)
    
    assert isinstance(decision, EventDecision)
    assert decision.action == EventAction.DROP
    assert decision.asset == valid_asset
    assert decision.should_produce_event() is True
    assert decision.should_save_asset() is True

def test_decide_invalid_event(event_service, valid_asset):
    """Test decision for invalid event."""
    invalid_event = Event(
        asset_id="123",
        event_type="INVALID",
        timestamp=datetime.now().isoformat(),
        metadata={}
    )
    
    decision = event_service.decide(invalid_event, valid_asset)
    
    assert isinstance(decision, EventDecision)
    assert decision.action == EventAction.NO_ACTION
    assert decision.asset == valid_asset
    assert decision.should_produce_event() is False
    assert decision.should_save_asset() is True

def test_decide_expired_event(event_service, valid_asset):
    """Test decision for expired event."""
    expired_event = Event(
        asset_id="123",
        event_type="UPSERT",
        timestamp="2020-01-01T00:00:00",
        metadata={"field1": "value1"}
    )
    
    decision = event_service.decide(expired_event, valid_asset)
    
    assert isinstance(decision, EventDecision)
    assert decision.action == EventAction.NO_ACTION
    assert decision.asset == valid_asset
    assert decision.should_produce_event() is False
    assert decision.should_save_asset() is True

def test_decide_missing_metadata(event_service):
    """Test decision for event with missing required metadata."""
    event_without_metadata = Event(
        asset_id="123",
        event_type="UPSERT",
        timestamp=datetime.now().isoformat(),
        metadata=None
    )
    
    decision = event_service.decide(event_without_metadata)
    
    assert isinstance(decision, EventDecision)
    assert decision.action == EventAction.NO_ACTION
    assert decision.should_produce_event() is False
    assert decision.should_save_asset() is True

def test_decide_duplicate_event(event_service, valid_event):
    """Test decision for duplicate event."""
    # Simula evento duplicado
    decision = event_service.decide(valid_event)
    second_decision = event_service.decide(valid_event)
    
    assert isinstance(second_decision, EventDecision)
    assert second_decision.action == EventAction.IGNORE
    assert second_decision.should_produce_event() is False
    assert second_decision.should_save_asset() is True
    assert "Duplicate event" in second_decision.reason 