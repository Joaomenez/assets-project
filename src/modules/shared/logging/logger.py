"""
Configuração e utilitários de logging.
"""
from typing import Dict, Any, Optional
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths
import json

def setup_logger(service: str, level: str = "INFO") -> Logger:
    """
    Configura um logger do Powertools.
    
    Args:
        service: Nome do serviço
        level: Nível de log (default: INFO)
        
    Returns:
        Logger configurado
    """
    return Logger(
        service=service,
        level=level,
        correlation_id_path=correlation_paths.API_GATEWAY_REST
    )

def log_event(logger: Logger, event: Dict[str, Any], level: str = "INFO") -> None:
    """
    Loga um evento com formatação adequada.
    
    Args:
        logger: Logger do Powertools
        event: Evento a ser logado
        level: Nível do log (default: INFO)
    """
    try:
        # Tenta formatar o evento como JSON
        event_str = json.dumps(event, indent=2)
    except:
        event_str = str(event)
    
    log_method = getattr(logger, level.lower())
    log_method(
        "Evento recebido",
        extra={
            "event": event_str
        }
    )

def log_metric(logger: Logger, name: str, value: Any, unit: Optional[str] = None) -> None:
    """
    Loga uma métrica.
    
    Args:
        logger: Logger do Powertools
        name: Nome da métrica
        value: Valor da métrica
        unit: Unidade da métrica (opcional)
    """
    extra = {
        "metric_name": name,
        "metric_value": value
    }
    if unit:
        extra["metric_unit"] = unit
        
    logger.info(
        f"Métrica registrada: {name}",
        extra=extra
    ) 