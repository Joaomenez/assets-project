"""
Configuração base para funções Lambda.
"""
from typing import Any, Callable, Dict
from functools import wraps
import asyncio
from aws_lambda_powertools import Logger
from ddtrace import patch_all, tracer
from ..tracing.datadog_config import configure_datadog, datadog_trace

logger = Logger()

def setup_lambda():
    """
    Configura o ambiente Lambda com Datadog e outras ferramentas.
    Deve ser chamado no início de cada função Lambda.
    """
    # Configura o Datadog
    configure_datadog()
    
    # Configura outras ferramentas necessárias
    logger.info("Lambda configurado com Datadog")

def lambda_handler(service_name: str):
    """
    Decorator para handlers Lambda com suporte a Datadog.
    
    Args:
        service_name: Nome do serviço para o trace
    """
    def decorator(handler: Callable):
        @wraps(handler)
        @datadog_trace(service=service_name, name="lambda_handler")
        async def wrapper(event: Dict[str, Any], context: Any):
            try:
                # Configura o ambiente
                setup_lambda()
                
                # Adiciona contexto ao trace
                with tracer.current_span() as span:
                    span.set_tag("function_name", context.function_name)
                    span.set_tag("function_version", context.function_version)
                    span.set_tag("aws_request_id", context.aws_request_id)
                    
                # Executa o handler
                return await handler(event, context)
                
            except Exception as e:
                # Registra erro no trace
                with tracer.current_span() as span:
                    span.set_tag("error", True)
                    span.set_tag("error_type", type(e).__name__)
                    span.set_tag("error_message", str(e))
                    
                logger.exception("Erro no handler Lambda")
                raise
                
        return wrapper
    return decorator 