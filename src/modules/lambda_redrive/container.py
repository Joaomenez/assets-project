from typing import Dict
from ..shared.container.dependency_container import DependencyContainer
from .infrastructure.repositories.sqs_dlq_repository import SQSDLQRepository
from .application.use_cases.process_dlq_events import ProcessDLQEventsUseCase

class RedriveContainer(DependencyContainer):
    """
    Container de dependências para a lambda redrive
    """
    # Constantes para TTL do cache
    DLQ_REPOSITORY_TTL = 15  # 15 minutos - menor TTL pois lida com mensagens de erro
    
    def __init__(self, env_vars: Dict[str, str]):
        """
        Inicializa o container
        
        Parâmetros:
            env_vars: Variáveis de ambiente necessárias:
                - UPSERT_QUEUE_DLQ_URL
                - DROP_QUEUE_DLQ_URL
        """
        required_vars = [
            'UPSERT_QUEUE_DLQ_URL',
            'DROP_QUEUE_DLQ_URL'
        ]
        
        # Valida variáveis de ambiente
        for var in required_vars:
            if var not in env_vars:
                raise ValueError(f"Variável de ambiente {var} não encontrada")
                
        super().__init__(env_vars)
        
    def create_dlq_repository(self) -> SQSDLQRepository:
        """
        Cria o repositório DLQ com TTL de 15 minutos
        TTL menor pois lida com mensagens de erro que precisam ser reprocessadas
        """
        return self._get_or_create(
            'sqs_dlq_repository',
            lambda: SQSDLQRepository(),
            ttl_minutes=self.DLQ_REPOSITORY_TTL
        )
        
    def create_use_case(self) -> ProcessDLQEventsUseCase:
        """
        Cria o caso de uso principal
        Não usa TTL pois é leve e depende de outras instâncias
        """
        return ProcessDLQEventsUseCase(
            dlq_repository=self.create_dlq_repository()
        )
        
    def get_default_dlq_urls(self) -> list[str]:
        """
        Retorna as URLs padrão das DLQs
        """
        return [
            self.env['UPSERT_QUEUE_DLQ_URL'],
            self.env['DROP_QUEUE_DLQ_URL']
        ] 