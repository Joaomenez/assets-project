import json
import uuid
from datetime import datetime, UTC
from typing import Dict, Optional
import boto3
from ...domain.interfaces.event_storage import EventStorage

class S3EventStorage(EventStorage):
    """
    Implementação de armazenamento de eventos usando Amazon S3
    """
    def __init__(
        self,
        bucket_name: str,
        s3_client: Optional[boto3.client] = None
    ):
        """
        Inicializa o armazenamento S3
        
        Parâmetros:
            bucket_name: Nome do bucket S3
            s3_client: Cliente boto3 S3 (opcional, para injeção em testes)
        """
        self.bucket = bucket_name
        self.s3 = s3_client or boto3.client('s3')
        
    def store_event(self, event_type: str, payload: Dict) -> str:
        """
        Armazena um evento no S3 e retorna sua localização
        
        Parâmetros:
            event_type: Tipo do evento (upsert/drop)
            payload: Dados do evento a serem armazenados
            
        Retorno:
            str: URI do objeto no S3 (s3://bucket/key)
        """
        # Gera um nome único para o arquivo
        timestamp = datetime.now(UTC).strftime('%Y/%m/%d/%H/%M/%S')
        unique_id = str(uuid.uuid4())
        key = f"events/{event_type}/{timestamp}-{unique_id}.json"
        
        # Faz upload do payload como JSON
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(payload).encode('utf-8'),
            ContentType='application/json'
        )
        
        return f"s3://{self.bucket}/{key}" 