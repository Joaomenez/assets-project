from dataclasses import dataclass
from typing import Optional, Dict
from ...domain.entities.asset import Asset

@dataclass
class ProcessEventResult:
    event_type: str
    asset: Asset
    
    def to_dict(self) -> Dict:
        """
        Converte o resultado para dicionário (para serialização)
        """
        return {
            "event_type": self.event_type,
            "asset": {
                "technology_name": self.asset.technology_name,
                "instance_technology_name": self.asset.instance_technology_name,
                "asset_parent_name": self.asset.asset_parent_name,
                "asset_name": self.asset.asset_name,
                "aws_account_number": self.asset.aws_account_number,
                "hash_value": self.asset.hash_value,
                "correlation_id": self.asset.correlation_id,
                "created_at": self.asset.created_at.isoformat(),
                "updated_at": self.asset.updated_at.isoformat()
            }
        } 