import json
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError
from ...domain.interfaces.event_storage_reader import EventStorageReader

class EventNotFoundError(Exception):
    """Erro lançado quando o evento não é encontrado no S3"""
    pass

class InvalidLocationError(Exception):
    """Erro lançado quando a localização do evento é inválida"""
    pass

class S3EventReader(EventStorageReader):
    """
    Implementação de leitura de eventos do S3
    """
    def __init__(self, s3_client: Optional[boto3.client] = None):
        """
        Inicializa o leitor de eventos
        
        Parâmetros:
            s3_client: Cliente boto3 S3 (opcional, para injeção em testes)
        """
        self.s3 = s3_client or boto3.client('s3')
        
    def read_event(self, event_location: str) -> Dict:
        """
        Lê um evento do S3
        
        Parâmetros:
            event_location: URI do objeto no S3 (s3://bucket/key)
            
        Retorno:
            Dict: Payload completo do evento
            
        Raises:
            EventNotFoundError: Se o evento não for encontrado
            InvalidLocationError: Se a URI for inválida
        """
        try:
            # Extrai bucket e key da URI
            if not event_location.startswith('s3://'):
                raise InvalidLocationError(f"URI inválida: {event_location}")
                
            path = event_location.replace('s3://', '')
            bucket, key = path.split('/', 1)
            
            # Lê o objeto do S3
            response = self.s3.get_object(
                Bucket=bucket,
                Key=key
            )
            
            # Decodifica o conteúdo JSON
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise EventNotFoundError(f"Evento não encontrado: {event_location}")
            raise
        except (ValueError, IndexError):
            raise InvalidLocationError(f"URI inválida: {event_location}") 