"""
Container de dependências para o lambda upsert_asset_event_producer.
"""
from typing import Dict
from modules.shared.container.dependency_container import DependencyContainer
from .infrastructure.queues.sqs_message_consumer import SQSMessageConsumer
from .infrastructure.storage.s3_event_reader import S3EventReader
from .infrastructure.producers.kafka_event_producer import KafkaEventProducer
from .application.use_cases.process_upsert_events import ProcessUpsertEventsUseCase

class UpsertEventContainer:
    """Container de dependências para o lambda upsert_asset_event_producer."""
    
    def __init__(self):
        # Inicializa componentes de infraestrutura
        self.event_reader = S3EventReader()
        self.message_consumer = SQSMessageConsumer(self.event_reader)
        self.event_producer = KafkaEventProducer()
        
        # Inicializa caso de uso
        self.process_upsert_events_use_case = ProcessUpsertEventsUseCase(
            self.message_consumer,
            self.event_producer
        )

    def create_event_reader(self) -> S3EventReader:
        """
        Cria o leitor de eventos do S3 com TTL de 1 hora
        """
        return self._get_or_create(
            's3_event_reader',
            lambda: S3EventReader(),
            ttl_minutes=self.EVENT_READER_TTL
        )
        
    def create_message_consumer(self) -> SQSMessageConsumer:
        """
        Cria o consumidor de mensagens SQS
        Usa o mesmo TTL do event_reader pois depende dele
        """
        return self._get_or_create(
            'sqs_message_consumer',
            lambda: SQSMessageConsumer(
                event_reader=self.create_event_reader()
            ),
            ttl_minutes=self.EVENT_READER_TTL
        )
        
    def create_event_producer(self) -> KafkaEventProducer:
        """
        Cria o produtor de eventos Kafka com TTL de 30 minutos
        """
        return self._get_or_create(
            'kafka_event_producer',
            lambda: KafkaEventProducer(
                bootstrap_servers=self.env['KAFKA_BOOTSTRAP_SERVERS']
            ),
            ttl_minutes=self.KAFKA_PRODUCER_TTL
        )
        
    def create_use_case(self) -> ProcessUpsertEventsUseCase:
        """
        Cria o caso de uso principal
        Não usa TTL pois é leve e depende de outras instâncias
        """
        return ProcessUpsertEventsUseCase(
            message_queue=self.create_message_consumer(),
            event_producer=self.create_event_producer()
        ) 