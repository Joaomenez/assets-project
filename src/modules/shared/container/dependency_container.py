"""
Container base para injeção de dependências.
"""
from typing import Dict, Any, TypeVar, Callable, Optional
from datetime import datetime, timedelta
import boto3
from aws_lambda_powertools import Logger

logger = Logger()
T = TypeVar('T')

class DependencyContainer:
    """Container base para injeção de dependências com suporte a cache."""
    
    def __init__(self):
        """Inicializa o container."""
        self._instances: Dict[str, Any] = {}
        self._last_access: Dict[str, datetime] = {}
        self._ttl_minutes: Dict[str, int] = {}
    
    def register(self, key: str, instance: Any, ttl_minutes: Optional[int] = None) -> None:
        """
        Registra uma instância no container.
        
        Args:
            key: Chave única para a instância
            instance: Instância a ser registrada
            ttl_minutes: Tempo de vida em minutos (opcional)
        """
        self._instances[key] = instance
        self._last_access[key] = datetime.now()
        if ttl_minutes is not None:
            self._ttl_minutes[key] = ttl_minutes
            
        logger.debug(f"Instância registrada", extra={
            "key": key,
            "type": type(instance).__name__,
            "ttl": ttl_minutes
        })
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera uma instância do container.
        
        Args:
            key: Chave da instância
            
        Returns:
            Instância registrada ou None se não encontrada ou expirada
        """
        if key not in self._instances:
            return None
            
        # Verifica TTL
        if key in self._ttl_minutes:
            now = datetime.now()
            ttl = timedelta(minutes=self._ttl_minutes[key])
            if now - self._last_access[key] > ttl:
                self._remove(key)
                return None
                
        self._last_access[key] = datetime.now()
        return self._instances[key]
    
    def get_or_create(self, key: str, factory: Callable[[], T], ttl_minutes: Optional[int] = None) -> T:
        """
        Recupera uma instância do container ou cria uma nova se não existir.
        
        Args:
            key: Chave da instância
            factory: Função factory para criar nova instância
            ttl_minutes: Tempo de vida em minutos (opcional)
            
        Returns:
            Instância existente ou nova
        """
        instance = self.get(key)
        if instance is None:
            instance = factory()
            self.register(key, instance, ttl_minutes)
            
        return instance
    
    def _remove(self, key: str) -> None:
        """
        Remove uma instância do container.
        
        Args:
            key: Chave da instância
        """
        if key in self._instances:
            del self._instances[key]
            del self._last_access[key]
            if key in self._ttl_minutes:
                del self._ttl_minutes[key]
                
            logger.debug(f"Instância removida", extra={"key": key})
    
    def clear(self) -> None:
        """Limpa todas as instâncias do container."""
        self._instances.clear()
        self._last_access.clear()
        self._ttl_minutes.clear()
        logger.debug("Container limpo") 