from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Attribute:
    attribute_name: str
    data_type: str
    is_primary_key: bool
    is_nullable: bool
    default_value: Optional[str]
    comment_description: str

@dataclass
class IndexedField:
    indexed_field_composition: List[str]

@dataclass
class UpsertEvent:
    correlation_id: str
    status: str
    asset_name: str
    asset_parent_name: str
    asset_counts: str
    aws_account_number: str
    technology_service_name: str
    asset_type: str
    instance_technology_name: str
    attributes: List[Attribute]
    indexed_field_list: List[IndexedField]

    @classmethod
    def from_dict(cls, data: Dict) -> 'UpsertEvent':
        attributes = [
            Attribute(**attr) for attr in data.get('attributes', [])
        ]
        indexed_fields = [
            IndexedField(**field) for field in data.get('indexed_field_list', [])
        ]
        
        return cls(
            correlation_id=data['correlation_id'],
            status=data['status'],
            asset_name=data['asset_name'],
            asset_parent_name=data['asset_parent_name'],
            asset_counts=data['asset_counts'],
            aws_account_number=data['aws_account_number'],
            technology_service_name=data['technology_service_name'],
            asset_type=data['asset_type'],
            instance_technology_name=data['instance_technology_name'],
            attributes=attributes,
            indexed_field_list=indexed_fields
        ) 