import json
from typing import Dict, List, Optional
import boto3
from ...domain.interfaces.message_queue import MessageQueue
from ...domain.interfaces.event_storage_reader import EventStorageReader

class SQSMessageConsumer(MessageQueue):
    """
    Consumidor de mensagens SQS com suporte a leitura de eventos do S3
    """
    def __init__(
        self,
        event_reader: EventStorageReader,
        sqs_client: Optional[boto3.client] = None
    ):
        """
        Inicializa o consumidor
        
        Parâmetros:
            event_reader: Leitor de eventos do storage
            sqs_client: Cliente boto3 SQS (opcional, para injeção em testes)
        """
        self.event_reader = event_reader
        self.sqs = sqs_client or boto3.client('sqs')
        
    def receive_messages(self, queue_url: str, max_messages: int = 10) -> List[Dict]:
        """
        Recebe mensagens da fila e carrega seus eventos do S3
        
        Parâmetros:
            queue_url: URL da fila SQS
            max_messages: Número máximo de mensagens a receber
            
        Retorno:
            Lista de mensagens com eventos carregados do S3
        """
        # Recebe mensagens do SQS
        response = self.sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            MessageAttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        loaded_messages = []
        
        for message in messages:
            try:
                # Carrega o corpo da mensagem
                body = json.loads(message['Body'])
                
                # Lê o evento completo do S3
                event_location = body['event_location']
                event_data = self.event_reader.read_event(event_location)
                
                # Adiciona dados do SQS que precisamos preservar
                loaded_messages.append({
                    'MessageId': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle'],
                    'Body': event_data
                })
                
            except Exception as e:
                # Log do erro e continua processando outras mensagens
                print(f"Erro ao carregar evento: {str(e)}")
                continue
                
        return loaded_messages
        
    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        """
        Remove uma mensagem da fila
        
        Parâmetros:
            queue_url: URL da fila SQS
            receipt_handle: Receipt handle da mensagem
        """
        self.sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        ) 