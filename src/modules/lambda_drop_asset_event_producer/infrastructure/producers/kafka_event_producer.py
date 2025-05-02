import json
from kafka import KafkaProducer
from ...domain.interfaces.event_producer import EventProducer
from ...domain.entities.drop_event import DropEvent

class KafkaEventProducer(EventProducer):
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def produce_event(self, topic: str, event: DropEvent) -> None:
        # Converte o evento para dicionário
        event_dict = {
            'correlation_id': event.correlation_id,
            'status': event.status,
            'asset_name': event.asset_name,
            'asset_parent_name': event.asset_parent_name,
            'asset_counts': event.asset_counts,
            'aws_account_number': event.aws_account_number,
            'technology_service_name': event.technology_service_name,
            'asset_type': event.asset_type,
            'instance_technology_name': event.instance_technology_name
        }
        
        # Envia o evento para o tópico Kafka
        self.producer.send(topic, event_dict)
        self.producer.flush() 