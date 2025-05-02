"""
Interfaces base para manipulação de eventos.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
from enum import Enum
from dataclasses import dataclass

class EventType(Enum):
    """Tipos de eventos suportados."""
    KINESIS = "kinesis"
    SQS = "sqs"
    CLOUDWATCH = "cloudwatch"
    DYNAMODB = "dynamodb"
    S3 = "s3"
    SNS = "sns"
    API_GATEWAY = "api_gateway"

@dataclass
class EventMetadata:
    """Metadados do evento."""
    event_type: EventType
    source: str
    timestamp: str
    version: str

class EventValidator(Protocol):
    """Protocolo para validação de eventos."""
    def validate(self, event: Dict[str, Any]) -> bool:
        """
        Valida um evento.
        
        Args:
            event: Evento a ser validado
            
        Returns:
            True se válido, False caso contrário
        """
        ...

class EventStorage(ABC):
    """Interface base para armazenamento de eventos."""
    
    @abstractmethod
    async def store(self, event: Dict[str, Any], metadata: EventMetadata) -> None:
        """
        Armazena um evento.
        
        Args:
            event: Evento a ser armazenado
            metadata: Metadados do evento
        """
        pass

class EventStorageReader(ABC):
    """Interface base para leitura de eventos."""
    
    @abstractmethod
    async def read(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Lê um evento pelo ID.
        
        Args:
            event_id: ID do evento
            
        Returns:
            Evento encontrado ou None
        """
        pass

class EventConsumer(ABC):
    """Interface base para consumo de eventos."""
    
    @abstractmethod
    async def consume(self, event: Dict[str, Any], metadata: EventMetadata) -> None:
        """
        Consome um evento.
        
        Args:
            event: Evento a ser consumido
            metadata: Metadados do evento
        """
        pass

class EventProducer(ABC):
    """Interface base para produção de eventos."""
    
    @abstractmethod
    async def produce(self, event: Dict[str, Any], metadata: EventMetadata) -> None:
        """
        Produz um evento.
        
        Args:
            event: Evento a ser produzido
            metadata: Metadados do evento
        """
        pass 