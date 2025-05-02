from abc import ABC, abstractmethod
from typing import List
from ..entities.asset import Asset

class EventQueueProducer(ABC):
    """
    Interface para produtores de eventos para filas
    """
    @abstractmethod
    def send_upsert_event(self, asset: Asset) -> None:
        """
        Envia um evento de upsert para a fila apropriada
        
        Parâmetros:
            asset: Asset a ser enviado
        """
        pass
        
    @abstractmethod
    def send_drop_event(self, assets: List[Asset]) -> None:
        """
        Envia um evento de drop para a fila apropriada
        
        Parâmetros:
            assets: Lista de assets a serem enviados
        """
        pass 