from abc import ABC, abstractmethod
from ..entities.drop_event import DropEvent

class EventProducer(ABC):
    @abstractmethod
    def produce_event(self, topic: str, event: DropEvent) -> None:
        """
        Produz um evento para um tópico Kafka
        
        Parâmetros:
            topic: Nome do tópico Kafka
            event: Evento a ser produzido
        """
        pass 