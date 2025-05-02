from typing import Dict
from ..shared.container.dependency_container import DependencyContainer
from .infrastructure.queues.sqs_message_consumer import SQSMessageConsumer
from .infrastructure.storage.s3_event_reader import S3EventReader
from .infrastructure.producers.kafka_event_producer import KafkaEventProducer
from .application.use_cases.process_drop_events import ProcessDropEventsUseCase

class DropEventContainer(DependencyContainer):
    """
    Container de dependências para a lambda drop_asset_event_producer
    """
    # Constantes para TTL do cache
    KAFKA_PRODUCER_TTL = 30  # 30 minutos
    EVENT_READER_TTL = 60    # 1 hora
    
    def __init__(self, env_vars: Dict[str, str]):
        """
        Inicializa o container
        
        Parâmetros:
            env_vars: Variáveis de ambiente necessárias:
                - DROP_QUEUE_URL
                - KAFKA_TOPIC
                - KAFKA_BOOTSTRAP_SERVERS
        """
        required_vars = [
            'DROP_QUEUE_URL',
            'KAFKA_TOPIC',
            'KAFKA_BOOTSTRAP_SERVERS'
        ]
        
        # Valida variáveis de ambiente
        for var in required_vars:
            if var not in env_vars:
                raise ValueError(f"Variável de ambiente {var} não encontrada")
                
        super().__init__(env_vars)
        
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
        
    def create_use_case(self) -> ProcessDropEventsUseCase:
        """
        Cria o caso de uso principal
        Não usa TTL pois é leve e depende de outras instâncias
        """
        return ProcessDropEventsUseCase(
            message_queue=self.create_message_consumer(),
            event_producer=self.create_event_producer()
        ) 