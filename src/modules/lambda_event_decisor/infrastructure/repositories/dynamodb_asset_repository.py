from typing import List, Optional
from pynamodb.exceptions import DoesNotExist
from pynamodb.expressions.condition import Condition
from boto3.dynamodb.conditions import Key
from ...domain.entities.asset import Asset
from ...domain.entities.event import Event
from ...domain.interfaces.asset_repository import AssetRepository
from .asset_model import AssetModel

class DynamoDBAssetRepository(AssetRepository):
    def __init__(self):
        self.model = AssetModel
    
    def find_by_event(self, event: Event) -> Optional[Asset]:
        """
        Busca um asset baseado em um evento usando a estrutura de chaves do DynamoDB
        """
        partition_key = self._build_partition_key(event)
        sort_key = event.aws_account_number
        
        try:
            item = self.model.get(partition_key, sort_key)
            if item:
                return self._to_domain_entity(item)
            return None
        except self.model.DoesNotExist:
            return None
    
    def find_by_parent_path(self, event: Event) -> List[Asset]:
        """
        Busca assets pelo caminho do parent usando o índice do DynamoDB
        """
        parent_path = self._build_parent_path(event)
        
        # Usa o índice GSI1 para buscar por parent_path
        response = self.model.parent_path_index.query(
            KeyConditionExpression=Key('parent_path').eq(parent_path) & 
                                 Key('aws_account_number').eq(event.aws_account_number)
        )
        
        return [self._to_domain_entity(item) for item in response]
    
    def save(self, asset: Asset) -> None:
        """
        Salva o asset no DynamoDB
        """
        item = self._to_dynamo_item(asset)
        item.save()
    
    def _build_partition_key(self, event: Event) -> str:
        """
        Constrói a partition key no formato esperado pelo DynamoDB
        """
        return f"{event.technology_name}/{event.instance_technology_name}/{event.asset_parent_name}/{event.asset_name}"
    
    def _build_parent_path(self, event: Event) -> str:
        """
        Constrói o caminho do parent para busca no índice
        """
        return f"{event.technology_name}/{event.instance_technology_name}/{event.asset_parent_name}"
    
    def _to_domain_entity(self, item: AssetModel) -> Asset:
        """
        Converte um item do DynamoDB para uma entidade de domínio
        """
        return Asset(
            technology_name=item.technology_name,
            instance_technology_name=item.instance_technology_name,
            asset_parent_name=item.asset_parent_name,
            asset_name=item.asset_name,
            aws_account_number=item.aws_account_number,
            hash_value=item.hash_value,
            correlation_id=item.correlation_id,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    def _to_dynamo_item(self, asset: Asset) -> AssetModel:
        """
        Converte uma entidade de domínio para um item do DynamoDB
        """
        return AssetModel(
            partition_key=f"{asset.technology_name}/{asset.instance_technology_name}/{asset.asset_parent_name}/{asset.asset_name}",
            sort_key=asset.aws_account_number,
            parent_path=f"{asset.technology_name}/{asset.instance_technology_name}/{asset.asset_parent_name}",
            technology_name=asset.technology_name,
            instance_technology_name=asset.instance_technology_name,
            asset_parent_name=asset.asset_parent_name,
            asset_name=asset.asset_name,
            aws_account_number=asset.aws_account_number,
            hash_value=asset.hash_value,
            correlation_id=asset.correlation_id,
            created_at=asset.created_at,
            updated_at=asset.updated_at
        )

    def get_by_keys(self, partition_key: str, sort_key: str) -> Optional[Asset]:
        """
        Busca um asset por sua partition key e sort key
        """
        try:
            asset_model = self.model.get(partition_key, sort_key)
            return asset_model.to_entity()
        except DoesNotExist:
            return None
    
    def find_by_parent_and_account(self, parent_path: str, aws_account_number: str, correlation_id: str) -> List[Asset]:
        """
        Busca assets por parent path e conta AWS, excluindo o correlation_id especificado
        """
        # Cria a condição de busca
        condition = (
            self.model.correlation_id != correlation_id
        )
        
        # Realiza a query
        assets = []
        for asset_model in self.model.query(
            hash_key_condition=self.model.pk.startswith(parent_path),
            range_key_condition=self.model.sk == aws_account_number,
            filter_condition=condition
        ):
            assets.append(asset_model.to_entity())
        
        return assets 