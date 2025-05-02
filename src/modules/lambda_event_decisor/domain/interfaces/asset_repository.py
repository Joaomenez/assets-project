from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.asset import Asset
from ..entities.event import Event

class AssetRepository(ABC):
    @abstractmethod
    def find_by_event(self, event: Event) -> Optional[Asset]:
        """
        Busca um asset baseado em um evento
        
        Parâmetros:
            event: Evento contendo as informações de busca
            
        Retorno:
            Asset encontrado ou None se não existir
        """
        pass
    
    @abstractmethod
    def find_by_parent_path(self, event: Event) -> List[Asset]:
        """
        Busca assets pelo caminho do parent e conta AWS
        
        Parâmetros:
            event: Evento contendo as informações de busca
            
        Retorno:
            Lista de assets encontrados
        """
        pass
    
    @abstractmethod
    def save(self, asset: Asset) -> None:
        """
        Salva ou atualiza um asset
        
        Parâmetros:
            asset: Asset a ser salvo
        """
        pass 