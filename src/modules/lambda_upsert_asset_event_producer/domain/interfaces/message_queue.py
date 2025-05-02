from abc import ABC, abstractmethod
from typing import List, Dict
from ..entities.upsert_event import UpsertEvent

class MessageQueue(ABC):
    @abstractmethod
    def receive_messages(self, queue_url: str, max_messages: int = 10) -> List[Dict]:
        """
        Recebe mensagens da fila SQS
        
        Parâmetros:
            queue_url: URL da fila SQS
            max_messages: Número máximo de mensagens a serem recebidas
        """
        pass
    
    @abstractmethod
    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        """
        Remove uma mensagem da fila SQS
        
        Parâmetros:
            queue_url: URL da fila SQS
            receipt_handle: Receipt handle da mensagem
        """
        pass 