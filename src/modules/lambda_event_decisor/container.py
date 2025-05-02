"""
Container de dependências para o lambda event_decisor.
"""
from typing import Dict
from modules.shared.container.dependency_container import DependencyContainer
from .infrastructure.repositories.dynamodb_asset_repository import DynamoDBAssetRepository
from .infrastructure.producers.sqs_event_producer import SQSEventProducer
from .infrastructure.storage.s3_event_storage import S3EventStorage
from .infrastructure.consumers.kinesis_stream_consumer import KinesisStreamConsumer
from .application.use_cases.process_event import ProcessEventUseCase
from .domain.services.event_decision_service import EventDecisionService
from .domain.services.hash_generator_service import HashGeneratorService

class EventDecisionContainer:
    """Container de dependências para o lambda event_decisor."""
    
    def __init__(self):
        # Inicializa repositórios e serviços
        self.asset_repository = DynamoDBAssetRepository()
        self.event_storage = S3EventStorage()
        self.event_producer = SQSEventProducer(self.event_storage)
        self.stream_consumer = KinesisStreamConsumer()
        
        # Inicializa serviços de domínio
        self.hash_generator_service = HashGeneratorService()
        self.event_decision_service = EventDecisionService(
            self.asset_repository,
            self.hash_generator_service
        )
        
        # Inicializa caso de uso
        self.process_event_use_case = ProcessEventUseCase(
            self.asset_repository,
            self.event_producer,
            self.event_decision_service
        )

    def create_repository(self) -> DynamoDBAssetRepository:
        """
        Cria o repositório DynamoDB com TTL de 1 hora
        """
        return self._get_or_create(
            'dynamodb_repository',
            lambda: DynamoDBAssetRepository(
                table_name=self.env['DYNAMODB_TABLE_NAME'],
                dynamodb_client=self._create_boto3_client('dynamodb')
            ),
            ttl_minutes=self.REPOSITORY_TTL
        )
        
    def create_event_storage(self) -> S3EventStorage:
        """
        Cria o storage de eventos S3 com TTL de 1 hora
        """
        return self._get_or_create(
            's3_event_storage',
            lambda: S3EventStorage(
                bucket_name=self.env['EVENTS_BUCKET_NAME'],
                s3_client=self._create_boto3_client('s3')
            ),
            ttl_minutes=self.EVENT_STORAGE_TTL
        )
        
    def create_event_producer(self) -> SQSEventProducer:
        """
        Cria o produtor de eventos SQS
        Não usa TTL pois é leve e dependente do storage
        """
        return SQSEventProducer(
            upsert_queue_url=self.env['UPSERT_QUEUE_URL'],
            drop_queue_url=self.env['DROP_QUEUE_URL'],
            event_storage=self.create_event_storage(),
            sqs_client=self._create_boto3_client('sqs')
        )
        
    def create_stream_consumer(self) -> KinesisStreamConsumer:
        """
        Cria o consumidor de eventos Kinesis
        Não usa TTL pois é stateless
        """
        return KinesisStreamConsumer()
        
    def create_use_case(self) -> ProcessEventUseCase:
        """
        Cria o caso de uso principal
        Não usa TTL pois é leve e dependente
        """
        return ProcessEventUseCase(
            asset_repository=self.create_repository(),
            event_queue_producer=self.create_event_producer()
        ) 