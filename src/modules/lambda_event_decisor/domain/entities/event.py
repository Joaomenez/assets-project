from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    technology_name: str
    instance_technology_name: str
    asset_parent_name: str
    asset_name: str
    aws_account_number: str
    status: str
    correlation_id: str
    metadata: dict
    
    @property
    def hash_value(self) -> str:
        """Gera um hash único baseado nos metadados do evento"""
        import hashlib
        import json
        
        metadata_str = json.dumps(self.metadata, sort_keys=True)
        return hashlib.sha256(metadata_str.encode()).hexdigest() 