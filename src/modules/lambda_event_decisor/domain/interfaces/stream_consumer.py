from abc import ABC, abstractmethod
from typing import List, Dict, Any

class StreamConsumer(ABC):
    """
    Interface para consumo de eventos de streams
    """
    @abstractmethod
    def parse_events(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os registros do stream e retorna os eventos parseados
        
        Parâmetros:
            records: Lista de registros do stream
            
        Retorno:
            Lista de eventos parseados
        """
        pass
        
    @abstractmethod
    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Valida se um evento está no formato correto
        
        Parâmetros:
            event: Evento a ser validado
            
        Retorno:
            True se o evento é válido, False caso contrário
        """
        pass 