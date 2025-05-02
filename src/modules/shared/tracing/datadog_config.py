"""
Configuração do Datadog para tracing distribuído.
"""
from typing import Optional, Dict, Any
from ddtrace import patch_all, tracer
from aws_lambda_powertools import Logger
from functools import wraps
import os
import asyncio

logger = Logger()

def configure_datadog():
    """
    Configura o Datadog para tracing.
    Deve ser chamado no início da aplicação.
    """
    # Configura variáveis de ambiente do Datadog
    os.environ['DD_TRACE_ENABLED'] = 'true'
    os.environ['DD_LOGS_INJECTION'] = 'true'
    os.environ['DD_RUNTIME_METRICS_ENABLED'] = 'true'
    
    # Patch automático de bibliotecas comuns
    patch_all()
    
    # Configura o tracer
    tracer.configure(
        hostname=os.getenv('DD_AGENT_HOST', 'localhost'),
        port=int(os.getenv('DD_TRACE_AGENT_PORT', 8126)),
        enabled=True
    )
    
    logger.info("Datadog configurado para tracing")

def datadog_trace(service: Optional[str] = None, name: Optional[str] = None, resource: Optional[str] = None):
    """
    Decorator para adicionar tracing do Datadog em funções.
    
    Args:
        service: Nome do serviço (opcional)
        name: Nome do span (opcional)
        resource: Nome do recurso (opcional)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracer.trace(
                span_name,
                service=service,
                resource=resource
            ) as span:
                # Adiciona informações do contexto AWS Lambda se disponível
                if 'context' in kwargs:
                    context = kwargs['context']
                    span.set_tag('function_name', context.function_name)
                    span.set_tag('function_version', context.function_version)
                    span.set_tag('memory_limit', context.memory_limit_in_mb)
                    span.set_tag('aws_request_id', context.aws_request_id)
                
                return await func(*args, **kwargs)
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracer.trace(
                span_name,
                service=service,
                resource=resource
            ) as span:
                if 'context' in kwargs:
                    context = kwargs['context']
                    span.set_tag('function_name', context.function_name)
                    span.set_tag('function_version', context.function_version)
                    span.set_tag('memory_limit', context.memory_limit_in_mb)
                    span.set_tag('aws_request_id', context.aws_request_id)
                
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def add_trace_context(span: Any, metadata: Dict[str, Any]) -> None:
    """
    Adiciona contexto ao span atual.
    
    Args:
        span: Span do Datadog
        metadata: Dicionário com metadados para adicionar ao span
    """
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            span.set_tag(key, value)
        else:
            try:
                span.set_tag(key, str(value))
            except:
                logger.warning(f"Não foi possível adicionar tag {key} ao span") 