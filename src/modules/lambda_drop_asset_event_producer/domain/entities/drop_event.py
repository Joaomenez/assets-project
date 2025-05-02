from dataclasses import dataclass
from typing import Dict

@dataclass
class DropEvent:
    correlation_id: str
    status: str
    asset_name: str
    asset_parent_name: str
    asset_counts: str
    aws_account_number: str
    technology_service_name: str
    asset_type: str
    instance_technology_name: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'DropEvent':
        return cls(
            correlation_id=data['correlation_id'],
            status=data['status'],
            asset_name=data['asset_name'],
            asset_parent_name=data['asset_parent_name'],
            asset_counts=data['asset_counts'],
            aws_account_number=data['aws_account_number'],
            technology_service_name=data['technology_service_name'],
            asset_type=data['asset_type'],
            instance_technology_name=data['instance_technology_name']
        ) 