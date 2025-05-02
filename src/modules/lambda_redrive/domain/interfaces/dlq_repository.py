from abc import ABC, abstractmethod
from typing import List
from ..entities.dlq_event import DLQEvent

class DLQRepository(ABC):
    @abstractmethod
    def get_events(self, queue_url: str, max_messages: int = 10) -> List[DLQEvent]:
        """
        Obtém eventos da DLQ
        
        Parâmetros:
            queue_url: URL da fila DLQ
            max_messages: Número máximo de mensagens a serem obtidas
        """
        pass
    
    @abstractmethod
    def move_to_original_queue(self, event: DLQEvent) -> None:
        """
        Move um evento da DLQ para sua fila original
        
        Parâmetros:
            event: Evento a ser movido
        """
        pass
    
    @abstractmethod
    def delete_from_dlq(self, event: DLQEvent) -> None:
        """
        Remove um evento da DLQ
        
        Parâmetros:
            event: Evento a ser removido
        """
        pass 