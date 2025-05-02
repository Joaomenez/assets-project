import hashlib
import json
from typing import Dict
from ..entities.event import Event

class HashGeneratorService:
    @staticmethod
    def generate_hash(event: Event) -> str:
        """
        Gera um hash para o evento baseado em seus atributos relevantes
        
        Parâmetros:
            event: Evento para gerar o hash
            
        Retorno:
            String contendo o hash SHA-256 do evento
        """
        # Cria um dicionário com os campos relevantes para o hash
        hash_content = {
            "technology_name": event.technology_name,
            "instance_technology_name": event.instance_technology_name,
            "asset_parent_name": event.asset_parent_name,
            "asset_name": event.asset_name,
            "aws_account_number": event.aws_account_number,
            "metadata": event.metadata  # Inclui os metadados pois podem conter informações estruturais
        }
        
        # Converte para string de forma determinística (ordena as chaves)
        content_str = json.dumps(hash_content, sort_keys=True)
        
        # Gera o hash SHA-256
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest() 