"""
Handler principal que roteia eventos para os handlers específicos.
"""
import os
from typing import Dict, Any
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.metrics import MetricUnit

from modules.shared.routing.event_router import EventRouter, EventType
from modules.lambda_event_decisor.presentation.handlers.event_decisor_handler import handler as event_decisor_handler
from modules.lambda_upsert_asset_event_producer.presentation.handlers.upsert_handler import handler as upsert_handler
from modules.lambda_drop_asset_event_producer.presentation.handlers.drop_handler import handler as drop_handler
from modules.lambda_redrive.presentation.handlers.redrive_handler import handler as redrive_handler

# Inicializa utilitários do Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace="MetadataProcessor")

# Inicializa o roteador
router = EventRouter()

# Registra os handlers
router.register(EventType.KINESIS, event_decisor_handler)
router.register(EventType.SQS, lambda e, c: upsert_handler(e, c) if 'UPSERT' in str(e) else drop_handler(e, c))
router.register(EventType.CLOUDWATCH, redrive_handler)

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
async def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Handler principal que roteia eventos para os handlers específicos
    
    Args:
        event: Evento recebido pela Lambda
        context: Contexto da Lambda
        
    Returns:
        Resultado do processamento
    """
    try:
        # Adiciona métricas
        metrics.add_metric(name="EventsReceived", unit=MetricUnit.Count, value=1)
        
        # Roteia o evento
        result = await router.route(event, context)
        
        # Adiciona métricas de sucesso
        metrics.add_metric(name="EventsProcessedSuccess", unit=MetricUnit.Count, value=1)
        
        return result
        
    except Exception as e:
        # Adiciona métricas de erro
        metrics.add_metric(name="EventsProcessedError", unit=MetricUnit.Count, value=1)
        
        # Log do erro
        logger.exception("Error processing event")
        
        # Retorna erro formatado
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Error processing event'
            }
        } 