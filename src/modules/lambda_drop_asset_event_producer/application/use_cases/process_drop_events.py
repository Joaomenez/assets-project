import json
from typing import Dict
from ...domain.interfaces.message_queue import MessageQueue
from ...domain.interfaces.event_producer import EventProducer
from ...domain.entities.drop_event import DropEvent

class ProcessDropEventsUseCase:
    def __init__(self, message_queue: MessageQueue, event_producer: EventProducer):
        self.message_queue = message_queue
        self.event_producer = event_producer
    
    def execute(self, queue_url: str, kafka_topic: str) -> Dict:
        """
        Processa eventos da fila SQS e produz para o Kafka
        
        Parâmetros:
            queue_url: URL da fila SQS
            kafka_topic: Tópico Kafka de destino
        
        Retorno:
            Dicionário com o resultado do processamento
        """
        results = {
            'processed': 0,
            'errors': []
        }
        
        try:
            # Recebe mensagens da fila SQS
            messages = self.message_queue.receive_messages(queue_url)
            
            for message in messages:
                try:
                    # Converte a mensagem em um evento
                    event_data = json.loads(message['Body'])
                    event = DropEvent.from_dict(event_data)
                    
                    # Produz o evento para o Kafka
                    self.event_producer.produce_event(kafka_topic, event)
                    
                    # Remove a mensagem da fila SQS
                    self.message_queue.delete_message(queue_url, message['ReceiptHandle'])
                    
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append({
                        'message_id': message.get('MessageId'),
                        'error': str(e)
                    })
                    
        except Exception as e:
            results['errors'].append({
                'error': str(e)
            })
        
        return results 