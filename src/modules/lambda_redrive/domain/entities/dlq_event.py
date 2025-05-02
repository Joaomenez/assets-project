from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class DLQEvent:
    message_id: str
    queue_url: str
    original_queue_url: str
    body: Dict
    retry_count: int = 0
    
    @property
    def has_exceeded_retries(self) -> bool:
        """Verifica se o evento excedeu o número máximo de tentativas"""
        return self.retry_count >= 5
    
    def increment_retry_count(self) -> None:
        """Incrementa o contador de tentativas"""
        self.retry_count += 1 