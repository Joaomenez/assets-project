"""
Módulo compartilhado para funcionalidades AWS.
Contém classes e utilitários para interação com serviços AWS.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class AWSClientCache:
    """
    Cache para clientes AWS com TTL.
    """
    def __init__(self, ttl_minutes: int = 60):
        self._cache: Dict[str, Any] = {}
        self._last_access: Dict[str, datetime] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        if datetime.now() - self._last_access[key] > self._ttl:
            del self._cache[key]
            del self._last_access[key]
            return None
        
        self._last_access[key] = datetime.now()
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._last_access[key] = datetime.now()

    def clear(self) -> None:
        self._cache.clear()
        self._last_access.clear() 