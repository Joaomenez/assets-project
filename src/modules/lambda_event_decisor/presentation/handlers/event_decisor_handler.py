"""
Handler principal para o lambda de decisão de eventos.
"""
from typing import Dict, Any
import asyncio
from aws_lambda_powertools.utilities.typing import LambdaContext
from ddtrace import tracer

from ....shared.config.lambda_config import lambda_handler
from ...container import EventDecisionContainer

@lambda_handler(service_name="event_decisor")
async def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Handler principal para processamento de decisão de eventos.
    
    Args:
        event: Evento Lambda recebido
        context: Contexto da execução Lambda
    
    Returns:
        Dict contendo o resultado do processamento
    """
    try:
        with tracer.current_span() as span:
            # Inicializa container
            container = EventDecisionContainer()
            span.set_tag("container_initialized", True)
            
            results = []
            # Processa cada registro do evento
            for record in event.get('Records', []):
                with tracer.trace("process_event") as event_span:
                    event_span.set_tag("event_source", record.get('eventSource', 'unknown'))
                    
                    result = await container.process_event_use_case.execute(record)
                    results.append(result)
                    
                    event_span.set_tag("processing_status", "success")
            
            response = {
                'statusCode': 200,
                'body': {
                    'message': 'Eventos processados com sucesso',
                    'processed_count': len(results)
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