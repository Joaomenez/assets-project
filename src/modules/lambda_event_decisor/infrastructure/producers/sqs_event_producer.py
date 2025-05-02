import json
from typing import List, Optional
import boto3
from ...domain.interfaces.event_queue_producer import EventQueueProducer
from ...domain.interfaces.event_storage import EventStorage
from ...domain.entities.asset import Asset
from ...domain.enums.event_action import EventAction

class SQSEventProducer(EventQueueProducer):
    """
    Implementação do produtor de eventos usando Amazon SQS com armazenamento S3
    """
    def __init__(
        self,
        upsert_queue_url: str,
        drop_queue_url: str,
        event_storage: EventStorage,
        sqs_client: Optional[boto3.client] = None
    ):
        """
        Inicializa o produtor de eventos
        
        Parâmetros:
            upsert_queue_url: URL da fila SQS para eventos de upsert
            drop_queue_url: URL da fila SQS para eventos de drop
            event_storage: Serviço de armazenamento de eventos
            sqs_client: Cliente boto3 SQS (opcional, para injeção em testes)
        """
        self.upsert_queue_url = upsert_queue_url
        self.drop_queue_url = drop_queue_url
        self.event_storage = event_storage
        self.sqs = sqs_client or boto3.client('sqs')
        
    def send_upsert_event(self, asset: Asset) -> None:
        """
        Armazena e envia um evento de upsert
        
        Parâmetros:
            asset: Asset a ser enviado
        """
        # Prepara o payload completo
        payload = {
            'event_type': str(EventAction.UPSERT),
            'asset': asset.to_dict()
        }
        
        # Armazena no S3 e obtém a localização
        event_location = self.event_storage.store_event('upsert', payload)
        
        # Envia mensagem SQS com referência ao evento
        message = {
            'event_type': str(EventAction.UPSERT),
            'event_location': event_location
        }
        
        self.sqs.send_message(
            QueueUrl=self.upsert_queue_url,
            MessageBody=json.dumps(message)
        )
        
    def send_drop_event(self, assets: List[Asset]) -> None:
        """
        Armazena e envia um evento de drop
        
        Parâmetros:
            assets: Lista de assets a serem enviados
        """
        # Prepara o payload completo
        payload = {
            'event_type': str(EventAction.DROP),
            'assets': [asset.to_dict() for asset in assets]
        }
        
        # Armazena no S3 e obtém a localização
        event_location = self.event_storage.store_event('drop', payload)
        
        # Envia mensagem SQS com referência ao evento
        message = {
            'event_type': str(EventAction.DROP),
            'event_location': event_location
        }
        
        self.sqs.send_message(
            QueueUrl=self.drop_queue_url,
            MessageBody=json.dumps(message)
        ) 