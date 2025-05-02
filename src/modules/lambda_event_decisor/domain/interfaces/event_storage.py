from abc import ABC, abstractmethod
from typing import Dict
from ..entities.asset import Asset

class EventStorage(ABC):
    """
    Interface para armazenamento de eventos
    """
    @abstractmethod
    def store_event(self, event_type: str, payload: Dict) -> str:
        """
        Armazena um evento e retorna sua localização
        
        Parâmetros:
            event_type: Tipo do evento (upsert/drop)
            payload: Dados do evento a serem armazenados
            
        Retorno:
            str: Identificador único da localização do evento (ex: s3://bucket/key)
        """
        pass 