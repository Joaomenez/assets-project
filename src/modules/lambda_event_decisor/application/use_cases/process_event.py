from typing import Optional
from ...domain.entities.event import Event
from ...domain.entities.asset import Asset
from ...domain.interfaces.asset_repository import AssetRepository
from ...domain.interfaces.event_queue_producer import EventQueueProducer
from ...domain.services.event_decision_service import EventDecisionService

class ProcessEventUseCase:
    def __init__(self, 
                 asset_repository: AssetRepository,
                 event_queue_producer: EventQueueProducer):
        self.asset_repository = asset_repository
        self.event_queue_producer = event_queue_producer
        self.decision_service = EventDecisionService()

    def execute(self, event: Event) -> None:
        """
        Processa um evento e decide qual ação tomar
        
        Parâmetros:
            event: Evento a ser processado
        """
        # Busca o asset existente
        existing_asset = self.asset_repository.find_by_event(event)
        
        # Obtém a decisão do serviço de domínio
        decision = self.decision_service.decide_event_action(event, existing_asset)
        
        # Salva o asset se necessário
        if decision.should_save_asset():
            self.asset_repository.save(decision.asset)
        
        # Produz evento se necessário
        if decision.is_upsert():
            self.event_queue_producer.send_upsert_event([decision.asset])
        elif decision.is_drop():
            self.event_queue_producer.send_drop_event([decision.asset])
    
