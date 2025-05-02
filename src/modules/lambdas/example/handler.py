"""
Exemplo de handler Lambda com tracing Datadog.
"""
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from ddtrace import tracer

from ...shared.config.lambda_config import lambda_handler
from ...shared.routing.event_router import EventRouter
from ...shared.events.interfaces import EventType
from ...shared.events.validators import SQSEventValidator

# Inicializa o router
router = EventRouter()

@tracer.wrap(service="example_processor", name="process_message")
async def process_message(event: Dict[str, Any], context: LambdaContext, metadata: Any) -> Dict[str, Any]:
    """
    Processa uma mensagem.
    
    Args:
        event: Evento recebido
        context: Contexto Lambda
        metadata: Metadados do evento
        
    Returns:
        Resultado do processamento
    """
    with tracer.current_span() as span:
        # Adiciona tags ao span
        span.set_tag("event_source", metadata.source)
        span.set_tag("event_type", metadata.event_type.value)
        
        # Simula processamento
        result = {
            "processed": True,
            "message_id": event['Records'][0].get('messageId', 'unknown'),
            "timestamp": metadata.timestamp
        }
        
        span.set_tag("result_status", "success")
        return result

@tracer.wrap(service="example_processor", name="audit_message")
async def audit_message(event: Dict[str, Any], context: LambdaContext, metadata: Any) -> Dict[str, Any]:
    """
    Audita uma mensagem.
    
    Args:
        event: Evento recebido
        context: Contexto Lambda
        metadata: Metadados do evento
        
    Returns:
        Resultado da auditoria
    """
    with tracer.current_span() as span:
        # Adiciona tags ao span
        span.set_tag("event_source", metadata.source)
        span.set_tag("event_type", metadata.event_type.value)
        
        # Simula auditoria
        result = {
            "audited": True,
            "message_id": event['Records'][0].get('messageId', 'unknown'),
            "timestamp": metadata.timestamp
        }
        
        span.set_tag("audit_status", "success")
        return result

# Registra handlers no router
router.register(
    event_type=EventType.SQS,
    handler=process_message,
    validator=SQSEventValidator()
)

router.register(
    event_type=EventType.SQS,
    handler=audit_message
)

@lambda_handler(service_name="example_lambda")
async def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Handler principal da Lambda.
    
    Args:
        event: Evento recebido
        context: Contexto Lambda
        
    Returns:
        Resultado do processamento
    """
    # O decorator lambda_handler já configura o ambiente e o tracing
    results = await router.route(event, context)
    
    # Combina os resultados
    combined_result = {
        "processed": any(r.get("processed", False) for r in results),
        "audited": any(r.get("audited", False) for r in results),
        "message_ids": [r.get("message_id") for r in results if "message_id" in r],
        "timestamp": results[0].get("timestamp") if results else None
    }
    
    with tracer.current_span() as span:
        span.set_tag("processing_status", "success")
        span.set_tag("messages_processed", len(combined_result["message_ids"]))
    
    return combined_result 