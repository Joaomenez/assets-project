from datetime import datetime, UTC
from typing import Dict, Optional
from ..entities.event import Event
from ..entities.asset import Asset
from ..interfaces.asset_repository import AssetRepository
from ..value_objects.event_decision import EventDecision
from .hash_generator_service import HashGeneratorService

class EventDecisionService:
    def __init__(self):
        self.hash_generator = HashGeneratorService()

    def decide_event_action(self, event: Event, existing_asset: Optional[Asset]) -> EventDecision:
        """
        Decide qual ação tomar com base no evento e no asset existente
        
        Parâmetros:
            event: Evento a ser processado
            existing_asset: Asset existente (se houver)
            
        Retorno:
            EventDecision contendo a decisão e os dados do asset
        """
        current_time = datetime.now(UTC)
        event_hash = self.hash_generator.generate_hash(event)
        
        if not existing_asset:
            # Cria um novo asset usando o método de fábrica
            new_asset = Asset.create_from_event(event, event_hash, current_time)
            return EventDecision.upsert(new_asset)
            
        if existing_asset.has_changed(event_hash):
            # Atualiza o asset existente
            existing_asset.update_from_event(event, event_hash, current_time)
            return EventDecision.upsert(existing_asset)
            
        # Apenas atualização de timestamp
        existing_asset.updated_at = current_time
        return EventDecision.no_action(existing_asset)
