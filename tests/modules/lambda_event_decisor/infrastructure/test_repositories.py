import pytest
from datetime import datetime
from src.modules.lambda_event_decisor.infrastructure.repositories.dynamodb_asset_repository import DynamoDBAssetRepository
from src.modules.lambda_event_decisor.domain.entities.asset import Asset

@pytest.fixture
def dynamodb_repository(dynamodb):
    """Fixture para criar o repositório com DynamoDB mockado."""
    repository = DynamoDBAssetRepository()
    repository.create_table()  # Cria a tabela no DynamoDB local
    return repository

@pytest.fixture
def sample_asset():
    """Fixture para criar um asset de exemplo."""
    return Asset(
        asset_id="123",
        name="Test Asset",
        type="test_type",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        metadata={
            "field1": "value1",
            "field2": "value2"
        }
    )

def test_create_asset(dynamodb_repository, sample_asset):
    """Test asset creation in DynamoDB."""
    # Cria o asset
    result = dynamodb_repository.create(sample_asset)
    
    assert result is True
    
    # Verifica se foi criado
    saved_asset = dynamodb_repository.get_by_id(sample_asset.asset_id)
    assert saved_asset is not None
    assert saved_asset.asset_id == sample_asset.asset_id
    assert saved_asset.name == sample_asset.name
    assert saved_asset.type == sample_asset.type

def test_update_asset(dynamodb_repository, sample_asset):
    """Test asset update in DynamoDB."""
    # Primeiro cria o asset
    dynamodb_repository.create(sample_asset)
    
    # Atualiza o asset
    sample_asset.name = "Updated Name"
    result = dynamodb_repository.update(sample_asset)
    
    assert result is True
    
    # Verifica se foi atualizado
    updated_asset = dynamodb_repository.get_by_id(sample_asset.asset_id)
    assert updated_asset.name == "Updated Name"

def test_delete_asset(dynamodb_repository, sample_asset):
    """Test asset deletion from DynamoDB."""
    # Primeiro cria o asset
    dynamodb_repository.create(sample_asset)
    
    # Deleta o asset
    result = dynamodb_repository.delete(sample_asset.asset_id)
    
    assert result is True
    
    # Verifica se foi deletado
    deleted_asset = dynamodb_repository.get_by_id(sample_asset.asset_id)
    assert deleted_asset is None

def test_get_nonexistent_asset(dynamodb_repository):
    """Test getting a nonexistent asset."""
    asset = dynamodb_repository.get_by_id("nonexistent-id")
    assert asset is None

def test_update_nonexistent_asset(dynamodb_repository, sample_asset):
    """Test updating a nonexistent asset."""
    result = dynamodb_repository.update(sample_asset)
    assert result is False

def test_delete_nonexistent_asset(dynamodb_repository):
    """Test deleting a nonexistent asset."""
    result = dynamodb_repository.delete("nonexistent-id")
    assert result is False

def test_list_assets(dynamodb_repository, sample_asset):
    """Test listing assets with filters."""
    # Cria múltiplos assets
    dynamodb_repository.create(sample_asset)
    
    second_asset = Asset(
        asset_id="456",
        name="Second Asset",
        type="test_type",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        metadata={"field1": "value2"}
    )
    dynamodb_repository.create(second_asset)
    
    # Lista assets por tipo
    assets = dynamodb_repository.list(filters={"type": "test_type"})
    assert len(assets) == 2
    
    # Lista assets por metadata
    assets = dynamodb_repository.list(filters={"metadata.field1": "value1"})
    assert len(assets) == 1
    assert assets[0].asset_id == sample_asset.asset_id

def test_batch_operations(dynamodb_repository):
    """Test batch create/update/delete operations."""
    assets = [
        Asset(
            asset_id=f"batch-{i}",
            name=f"Batch Asset {i}",
            type="batch_type",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata={"batch": str(i)}
        )
        for i in range(3)
    ]
    
    # Batch create
    result = dynamodb_repository.batch_create(assets)
    assert result is True
    
    # Verifica se todos foram criados
    for asset in assets:
        saved_asset = dynamodb_repository.get_by_id(asset.asset_id)
        assert saved_asset is not None
        assert saved_asset.asset_id == asset.asset_id
    
    # Batch update
    for asset in assets:
        asset.name = f"Updated {asset.name}"
    result = dynamodb_repository.batch_update(assets)
    assert result is True
    
    # Batch delete
    asset_ids = [asset.asset_id for asset in assets]
    result = dynamodb_repository.batch_delete(asset_ids)
    assert result is True
    
    # Verifica se todos foram deletados
    for asset_id in asset_ids:
        assert dynamodb_repository.get_by_id(asset_id) is None 