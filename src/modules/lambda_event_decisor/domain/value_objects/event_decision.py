from dataclasses import dataclass
from typing import Optional
from ..entities.asset import Asset
from ..enums.event_action import EventAction

@dataclass
class EventDecision:
    action: EventAction
    asset: Asset
    
    @classmethod
    def upsert(cls, asset: Asset) -> 'EventDecision':
        return cls(action=EventAction.UPSERT, asset=asset)
    
    @classmethod
    def drop(cls, asset: Asset) -> 'EventDecision':
        return cls(action=EventAction.DROP, asset=asset)
    
    @classmethod
    def no_action(cls, asset: Asset) -> 'EventDecision':
        return cls(action=EventAction.NO_ACTION, asset=asset)
    
    def should_save_asset(self) -> bool:
        """Indica se o asset deve ser salvo no repositório"""
        return True  # Por enquanto sempre salvamos, mas podemos adicionar lógica aqui
    
    def should_produce_event(self) -> bool:
        """Indica se devemos produzir um evento para as filas"""
        return self.is_upsert() or self.is_drop()
        
    def is_upsert(self) -> bool:
        """
        Verifica se a decisão é de upsert
        
        Retorno:
            True se for uma ação de upsert, False caso contrário
        """
        return self.action == EventAction.UPSERT
        
    def is_drop(self) -> bool:
        """
        Verifica se a decisão é de drop
        
        Retorno:
            True se for uma ação de drop, False caso contrário
        """
        return self.action == EventAction.DROP
        
    def is_no_action(self) -> bool:
        """
        Verifica se a decisão é de não fazer nada
        
        Retorno:
            True se for uma ação de no_action, False caso contrário
        """
        return self.action == EventAction.NO_ACTION 