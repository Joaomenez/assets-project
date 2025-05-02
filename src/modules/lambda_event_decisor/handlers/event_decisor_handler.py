import json
import os
import boto3
from typing import Dict, Any

from ..application.use_cases.process_event import ProcessEventUseCase
from ..infrastructure.repositories.dynamodb_asset_repository import DynamoDBAssetRepository

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler da Lambda event-decisor
    
    Parâmetros:
        event: Evento da Lambda contendo os dados do evento a ser processado
        context: Contexto da execução da Lambda
    
    Retorno:
        Dicionário com o resultado do processamento
    """
    try:
        # Inicializa o repositório
        asset_repository = DynamoDBAssetRepository(
            table_name=os.environ['DYNAMODB_TABLE_NAME']
        )
        
        # Inicializa o caso de uso
        process_event_use_case = ProcessEventUseCase(asset_repository)
        
        # Processa o evento
        records = event.get('Records', [])
        
        responses = []
        for record in records:
            # Extrai o corpo da mensagem do SQS
            message_body = json.loads(record['body'])
            
            # Processa o evento
            result = process_event_use_case.execute(message_body)
            
            if result:
                # Se houver resultado, envia para a fila apropriada
                if result['event_type'] == 'upsert':
                    _send_to_queue(
                        queue_url=os.environ['UPSERT_QUEUE_URL'],
                        message=result['asset']
                    )
                elif result['event_type'] == 'drop':
                    _send_to_queue(
                        queue_url=os.environ['DROP_QUEUE_URL'],
                        message={'assets': result['assets']}
                    )
                
                responses.append(result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Eventos processados com sucesso',
                'results': responses
            })
        }
        
    except Exception as e:
        print(f"Erro ao processar evento: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def _send_to_queue(queue_url: str, message: Dict) -> None:
    """
    Envia uma mensagem para uma fila SQS
    
    Parâmetros:
        queue_url: URL da fila SQS
        message: Mensagem a ser enviada
    """
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    ) 