"""
Handler principal para o lambda de drop de assets.
"""
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from ddtrace import tracer
import os

from ....shared.config.lambda_config import lambda_handler
from ...container import DropEventContainer

@lambda_handler(service_name="drop_asset_producer")
async def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Handler principal para processamento de eventos de drop.
    
    Args:
        event: Evento Lambda recebido
        context: Contexto da execução Lambda
    
    Returns:
        Dict contendo o resultado do processamento
    """
    try:
        with tracer.current_span() as span:
            # Inicializa container com variáveis de ambiente
            container = DropEventContainer(dict(os.environ))
            span.set_tag("container_initialized", True)
            
            results = []
            # Processa cada registro do evento
            for record in event.get('Records', []):
                with tracer.trace("process_drop_event") as event_span:
                    # Extrai informações do evento DynamoDB
                    dynamodb_data = record.get('dynamodb', {})
                    event_name = record.get('eventName', 'UNKNOWN')
                    
                    # Apenas processa eventos REMOVE
                    if event_name != 'REMOVE':
                        event_span.set_tag("skipped", True)
                        event_span.set_tag("skip_reason", f"event_name={event_name}")
                        continue
                    
                    event_span.set_tag("event_name", event_name)
                    event_span.set_tag("sequence_number", dynamodb_data.get('SequenceNumber', 'unknown'))
                    
                    # Processa o evento
                    result = await container.process_drop_events_use_case.execute(
                        queue_url=container.env['DROP_QUEUE_URL'],
                        kafka_topic=container.env['KAFKA_TOPIC'],
                        record=record
                    )
                    results.append(result)
                    
                    event_span.set_tag("processing_status", "success")
            
            response = {
                'statusCode': 200,
                'body': {
                    'message': 'Eventos processados com sucesso',
                    'processed_count': len(results),
                    'results': results
                }
            }
            
            span.set_tag("processing_status", "success")
            span.set_tag("events_processed", len(results))
            
            return response
            
    except Exception as e:
        with tracer.current_span() as span:
            span.set_tag("error", True)
            span.set_tag("error_type", type(e).__name__)
            span.set_tag("error_message", str(e))
            
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Erro ao processar eventos'
            }
        } 