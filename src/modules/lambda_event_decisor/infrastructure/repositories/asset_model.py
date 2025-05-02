from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from datetime import datetime
from ...domain.entities.asset import Asset

class AssetModel(Model):
    """
    Modelo PynamoDB para a entidade Asset
    """
    class Meta:
        table_name = None  # Será definido dinamicamente
        region = 'us-east-1'  # Região padrão, pode ser sobrescrita
    
    # Chaves da tabela
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)
    
    # Atributos
    technology_name = UnicodeAttribute()
    instance_technology_name = UnicodeAttribute()
    asset_parent_name = UnicodeAttribute()
    asset_name = UnicodeAttribute()
    aws_account_number = UnicodeAttribute()
    hash_value = UnicodeAttribute()
    correlation_id = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    
    @classmethod
    def from_entity(cls, asset: Asset) -> 'AssetModel':
        """
        Cria uma instância do modelo a partir de uma entidade Asset
        """
        return cls(
            pk=asset.partition_key,
            sk=asset.sort_key,
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
    
    def to_entity(self) -> Asset:
        """
        Converte o modelo para uma entidade Asset
        """
        return Asset(
            technology_name=self.technology_name,
            instance_technology_name=self.instance_technology_name,
            asset_parent_name=self.asset_parent_name,
            asset_name=self.asset_name,
            aws_account_number=self.aws_account_number,
            hash_value=self.hash_value,
            correlation_id=self.correlation_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        ) 