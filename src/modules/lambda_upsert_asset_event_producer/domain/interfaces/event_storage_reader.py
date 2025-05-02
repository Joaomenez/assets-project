from abc import ABC, abstractmethod
from typing import Dict

class EventStorageReader(ABC):
    """
    Interface para leitura de eventos armazenados
    """
    @abstractmethod
    def read_event(self, event_location: str) -> Dict:
        """
        Lê um evento armazenado a partir de sua localização
        
        Parâmetros:
            event_location: Localização do evento (ex: s3://bucket/key)
            
        Retorno:
            Dict: Payload completo do evento
            
        Raises:
            EventNotFoundError: Se o evento não for encontrado
            InvalidLocationError: Se a localização for inválida
        """
        pass 