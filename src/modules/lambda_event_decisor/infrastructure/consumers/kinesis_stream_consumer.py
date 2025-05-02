import json
import base64
from typing import List, Dict, Any
from ...domain.interfaces.stream_consumer import StreamConsumer
from ....shared.logging.logger import setup_logger

class KinesisStreamConsumer(StreamConsumer):
    """
    Implementação do consumidor de eventos do Kinesis Data Stream
    """
    def __init__(self):
        """
        Inicializa o consumidor
        """
        self.logger = setup_logger(__name__)
        
    def parse_events(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os registros do Kinesis e retorna os eventos parseados
        
        Parâmetros:
            records: Lista de registros do Kinesis
            
        Retorno:
            Lista de eventos parseados
        """
        events = []
        
        for record in records:
            try:
                # Obtém os dados do registro
                kinesis_data = record.get('kinesis', {})
                if not kinesis_data:
                    self.logger.warning("Record without kinesis data", extra={'data': record})
                    continue
                    
                # Decodifica os dados do registro
                encoded_data = kinesis_data.get('data', '')
                if not encoded_data:
                    self.logger.warning("Kinesis record without data", extra={'data': kinesis_data})
                    continue
                    
                # Decodifica base64 e parse JSON
                json_str = base64.b64decode(encoded_data).decode('utf-8')
                event = json.loads(json_str)
                
                # Valida o evento
                if self.validate_event(event):
                    events.append(event)
                else:
                    self.logger.warning(
                        "Invalid event format",
                        extra={'data': {'event': event}}
                    )
                    
            except json.JSONDecodeError as e:
                self.logger.error(
                    "Error decoding JSON from Kinesis record",
                    exc_info=True,
                    extra={'data': {'error': str(e), 'record': record}}
                )
            except Exception as e:
                self.logger.error(
                    "Error processing Kinesis record",
                    exc_info=True,
                    extra={'data': {'error': str(e), 'record': record}}
                )
                
        return events
        
    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Valida se um evento está no formato correto
        
        Parâmetros:
            event: Evento a ser validado
            
        Retorno:
            True se o evento é válido, False caso contrário
        """
        required_fields = ['event_type', 'event_id', 'timestamp', 'data']
        
        # Verifica campos obrigatórios
        for field in required_fields:
            if field not in event:
                self.logger.warning(
                    f"Missing required field: {field}",
                    extra={'data': {'event': event}}
                )
                return False
                
        # Valida o tipo do evento
        if event['event_type'] not in ['UPSERT', 'DROP']:
            self.logger.warning(
                "Invalid event type",
                extra={'data': {'event_type': event['event_type']}}
            )
            return False
            
        return True 