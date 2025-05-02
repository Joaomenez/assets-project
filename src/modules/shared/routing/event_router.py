"""
Roteador de eventos para diferentes handlers.
"""
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from ddtrace import tracer

from ..events.interfaces import EventType, EventMetadata, EventValidator
from ..logging.logger import log_event
from ..tracing.datadog_config import datadog_trace, add_trace_context

logger = Logger()

class EventValidationError(Exception):
    """Erro de validação de evento."""
    pass

class HandlerNotFoundError(Exception):
    """Erro de handler não encontrado."""
    pass

class EventRouter:
    """Roteador de eventos para diferentes handlers."""
    
    def __init__(self):
        self._routes: Dict[EventType, List[Callable]] = {}
        self._validators: Dict[EventType, List[EventValidator]] = {}
    
    @datadog_trace(service="event_router", name="register_handler")
    def register(self, event_type: EventType, handler: Callable, validator: Optional[EventValidator] = None) -> None:
        """
        Registra um handler para um tipo de evento.
        
        Args:
            event_type: Tipo do evento
            handler: Função handler para processar o evento
            validator: Validador opcional para o evento
        """
        if event_type not in self._routes:
            self._routes[event_type] = []
            self._validators[event_type] = []
            
        self._routes[event_type].append(handler)
        if validator:
            self._validators[event_type].append(validator)
            
        with tracer.current_span() as span:
            add_trace_context(span, {
                "event_type": event_type.value,
                "handler_name": handler.__name__,
                "has_validator": validator is not None
            })
            
        logger.info("Handler registrado", extra={
            "event_type": event_type.value,
            "handler": handler.__name__,
            "has_validator": validator is not None
        })
    
    @datadog_trace(service="event_router", name="detect_event_type")
    def _detect_event_type(self, event: Dict[str, Any]) -> Optional[EventType]:
        """
        Detecta o tipo do evento baseado em sua estrutura.
        
        Args:
            event: Evento a ser analisado
            
        Returns:
            Tipo do evento detectado ou None
        """
        detected_type = None
        
        if 'Records' in event:
            record = event['Records'][0]
            if 'kinesis' in record:
                detected_type = EventType.KINESIS
            elif 'eventSource' in record:
                if record['eventSource'] == 'aws:sqs':
                    detected_type = EventType.SQS
                elif record['eventSource'] == 'aws:dynamodb':
                    detected_type = EventType.DYNAMODB
                elif record['eventSource'] == 'aws:s3':
                    detected_type = EventType.S3
                elif record['eventSource'] == 'aws:sns':
                    detected_type = EventType.SNS
        elif 'detail-type' in event and 'source' in event:
            detected_type = EventType.CLOUDWATCH
        elif 'requestContext' in event and 'httpMethod' in event:
            detected_type = EventType.API_GATEWAY
            
        with tracer.current_span() as span:
            add_trace_context(span, {
                "detected_event_type": detected_type.value if detected_type else "unknown"
            })
            
        return detected_type
    
    @datadog_trace(service="event_router", name="extract_metadata")
    def _extract_metadata(self, event: Dict[str, Any], event_type: EventType) -> EventMetadata:
        """
        Extrai metadados do evento.
        
        Args:
            event: Evento
            event_type: Tipo do evento
            
        Returns:
            Metadados do evento
        """
        source = ""
        if 'Records' in event and event['Records']:
            record = event['Records'][0]
            if 'eventSource' in record:
                source = record['eventSource']
            elif 'kinesis' in record:
                source = 'aws:kinesis'
        elif 'source' in event:
            source = event['source']
        elif 'requestContext' in event:
            source = 'api_gateway'
            
        metadata = EventMetadata(
            event_type=event_type,
            source=source,
            timestamp=datetime.utcnow().isoformat(),
            version='1.0'
        )
        
        with tracer.current_span() as span:
            add_trace_context(span, metadata.__dict__)
            
        return metadata
    
    @datadog_trace(service="event_router", name="validate_event")
    def _validate_event(self, event: Dict[str, Any], event_type: EventType) -> None:
        """
        Valida um evento usando os validadores registrados.
        
        Args:
            event: Evento a ser validado
            event_type: Tipo do evento
            
        Raises:
            EventValidationError: Se a validação falhar
        """
        if event_type not in self._validators:
            return
            
        with tracer.current_span() as span:
            span.set_tag("validation_count", len(self._validators[event_type]))
            
        for validator in self._validators[event_type]:
            if not validator.validate(event):
                with tracer.current_span() as span:
                    span.set_tag("validation_error", True)
                    span.set_tag("validator_class", validator.__class__.__name__)
                raise EventValidationError(f"Validação falhou para evento do tipo {event_type.value}")
    
    @datadog_trace(service="event_router", name="route_event")
    async def route(self, event: Dict[str, Any], context: LambdaContext) -> List[Dict[str, Any]]:
        """
        Roteia um evento para os handlers apropriados.
        
        Args:
            event: Evento a ser roteado
            context: Contexto da execução Lambda
            
        Returns:
            Lista com resultados do processamento
            
        Raises:
            ValueError: Se o tipo do evento não for reconhecido
            HandlerNotFoundError: Se não houver handler registrado
            EventValidationError: Se a validação do evento falhar
        """
        try:
            event_type = self._detect_event_type(event)
            if not event_type:
                with tracer.current_span() as span:
                    span.set_tag("error", "unknown_event_type")
                raise ValueError("Tipo de evento não reconhecido")
                
            metadata = self._extract_metadata(event, event_type)
            log_event(logger, event)
            
            self._validate_event(event, event_type)
            
            handlers = self._routes.get(event_type, [])
            if not handlers:
                with tracer.current_span() as span:
                    span.set_tag("error", "no_handlers_found")
                raise HandlerNotFoundError(f"Nenhum handler registrado para o tipo {event_type.value}")
            
            with tracer.current_span() as span:
                add_trace_context(span, {
                    "event_type": event_type.value,
                    "handlers_count": len(handlers),
                    "metadata": metadata.__dict__
                })
            
            logger.info("Roteando evento", extra={
                "event_type": event_type.value,
                "handlers_count": len(handlers),
                "metadata": metadata.__dict__
            })
            
            results = []
            for handler in handlers:
                with tracer.trace(f"handler.{handler.__name__}") as span:
                    add_trace_context(span, {
                        "handler_name": handler.__name__,
                        "event_type": event_type.value
                    })
                    result = await handler(event, context, metadata)
                    results.append(result)
            
            return results
            
        except Exception as e:
            with tracer.current_span() as span:
                span.set_tag("error", True)
                span.set_tag("error_type", type(e).__name__)
                span.set_tag("error_message", str(e))
                
            logger.error("Erro ao rotear evento", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "event": event
            })
            raise 