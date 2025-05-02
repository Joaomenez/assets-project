from abc import ABC, abstractmethod
from ..entities.upsert_event import UpsertEvent

class EventProducer(ABC):
    @abstractmethod
    def produce_event(self, topic: str, event: UpsertEvent) -> None:
        """
        Produz um evento para um tópico Kafka
        
        Parâmetros:
            topic: Nome do tópico Kafka
            event: Evento a ser produzido
        """
        pass 