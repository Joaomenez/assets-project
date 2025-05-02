"""
Handler principal para o lambda de redrive.
"""
from typing import Dict, Any, List
from aws_lambda_powertools.utilities.typing import LambdaContext
from ddtrace import tracer
import os

from ....shared.config.lambda_config import lambda_handler
from ...container import RedriveContainer

@lambda_handler(service_name="redrive_processor")
async def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Handler principal para processamento de eventos da DLQ.
    
    Args:
        event: Evento Lambda recebido
        context: Contexto da execução Lambda
    
    Returns:
        Dict contendo o resultado do processamento
    """
    try:
        with tracer.current_span() as span:
            # Inicializa container com variáveis de ambiente
            container = RedriveContainer(dict(os.environ))
            span.set_tag("container_initialized", True)
            
            # Obtém as URLs das DLQs do evento ou do container
            dlq_urls = event.get('dlq_urls', container.get_default_dlq_urls())
            span.set_tag("dlq_count", len(dlq_urls))
            
            results = []
            # Processa cada DLQ
            for dlq_url in dlq_urls:
                with tracer.trace("process_dlq") as dlq_span:
                    dlq_span.set_tag("dlq_url", dlq_url)
                    
                    # Processa os eventos da DLQ
                    result = await container.process_dlq_events_use_case.execute(dlq_url)
                    results.append(result)
                    
                    dlq_span.set_tag("processing_status", "success")
                    dlq_span.set_tag("messages_processed", len(result.get('messages', [])))
            
            # Combina os resultados
            combined_result = {
                'total_processed': sum(len(r.get('messages', [])) for r in results),
                'dlqs_processed': len(results),
                'results_per_dlq': results
            }
            
            response = {
                'statusCode': 200,
                'body': {
                    'message': 'Eventos processados com sucesso',
                    'results': combined_result
                }
            }
            
            span.set_tag("processing_status", "success")
            span.set_tag("total_messages", combined_result['total_processed'])
            span.set_tag("dlqs_processed", combined_result['dlqs_processed'])
            
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
                'message': 'Erro ao processar eventos da DLQ'
            }
        } 