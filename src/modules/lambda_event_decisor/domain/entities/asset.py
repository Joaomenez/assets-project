from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .event import Event

@dataclass
class Asset:
    technology_name: str
    instance_technology_name: str
    asset_parent_name: str
    asset_name: str
    aws_account_number: str
    hash_value: str
    correlation_id: str
    created_at: datetime
    updated_at: datetime
    
    @property
    def partition_key(self) -> str:
        return f"{self.technology_name}/{self.instance_technology_name}/{self.asset_parent_name}/{self.asset_name}"
    
    @property
    def sort_key(self) -> str:
        return self.aws_account_number 

    def has_changed(self, event_hash: str) -> bool:
        """
        Verifica se o asset mudou comparando com um novo hash
        
        Parâmetros:
            event_hash: Hash do evento para comparação
            
        Retorno:
            True se o asset mudou (hashes diferentes), False caso contrário
        """
        return self.hash_value != event_hash

    @classmethod
    def create_from_event(cls, event: Event, event_hash: str, timestamp: datetime) -> 'Asset':
        """
        Cria um novo Asset a partir de um Event
        
        Parâmetros:
            event: Evento fonte
            event_hash: Hash calculado do evento
            timestamp: Data/hora da criação
            
        Retorno:
            Nova instância de Asset
        """
        return cls(
            technology_name=event.technology_name,
            instance_technology_name=event.instance_technology_name,
            asset_parent_name=event.asset_parent_name,
            asset_name=event.asset_name,
            aws_account_number=event.aws_account_number,
            hash_value=event_hash,
            correlation_id=event.correlation_id,
            created_at=timestamp,
            updated_at=timestamp
        )
    
    def update_from_event(self, event: Event, event_hash: str, timestamp: datetime) -> None:
        """
        Atualiza o asset com informações do evento
        
        Parâmetros:
            event: Evento fonte
            event_hash: Hash calculado do evento
            timestamp: Data/hora da atualização
        """
        self.hash_value = event_hash
        self.correlation_id = event.correlation_id
        self.updated_at = timestamp 