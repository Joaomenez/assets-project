import json
import boto3
from typing import List, Dict
from ...domain.entities.dlq_event import DLQEvent
from ...domain.interfaces.dlq_repository import DLQRepository

class SQSDLQRepository(DLQRepository):
    def __init__(self):
        self.sqs = boto3.client('sqs')
    
    def get_events(self, queue_url: str, max_messages: int = 10) -> List[DLQEvent]:
        response = self.sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            MessageAttributeNames=['All'],
            AttributeNames=['All']
        )
        
        events = []
        for message in response.get('Messages', []):
            # Tenta obter o retry_count dos atributos da mensagem
            retry_count = 0
            if 'MessageAttributes' in message:
                retry_count_attr = message['MessageAttributes'].get('retry_count', {})
                if retry_count_attr.get('DataType') == 'Number':
                    retry_count = int(retry_count_attr['StringValue'])
            
            # Obtém a fila original dos atributos da mensagem
            original_queue_url = message['MessageAttributes'].get('original_queue_url', {}).get('StringValue')
            if not original_queue_url:
                # Se não encontrar nos atributos, assume que é a fila correspondente sem o -dlq
                original_queue_url = queue_url.replace('-dlq', '')
            
            events.append(DLQEvent(
                message_id=message['MessageId'],
                queue_url=queue_url,
                original_queue_url=original_queue_url,
                body=json.loads(message['Body']),
                retry_count=retry_count
            ))
        
        return events
    
    def move_to_original_queue(self, event: DLQEvent) -> None:
        # Incrementa o contador de tentativas
        event.increment_retry_count()
        
        # Envia para a fila original
        self.sqs.send_message(
            QueueUrl=event.original_queue_url,
            MessageBody=json.dumps(event.body),
            MessageAttributes={
                'retry_count': {
                    'DataType': 'Number',
                    'StringValue': str(event.retry_count)
                },
                'original_queue_url': {
                    'DataType': 'String',
                    'StringValue': event.original_queue_url
                }
            }
        )
    
    def delete_from_dlq(self, event: DLQEvent) -> None:
        # Obtém o receipt handle da mensagem
        response = self.sqs.receive_message(
            QueueUrl=event.queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            AttributeNames=['All'],
            VisibilityTimeout=30,
            WaitTimeSeconds=0
        )
        
        for message in response.get('Messages', []):
            if message['MessageId'] == event.message_id:
                self.sqs.delete_message(
                    QueueUrl=event.queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                break 