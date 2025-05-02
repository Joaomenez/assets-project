from typing import List, Dict
from ...domain.interfaces.dlq_repository import DLQRepository

class ProcessDLQEventsUseCase:
    def __init__(self, dlq_repository: DLQRepository):
        self.dlq_repository = dlq_repository
    
    def execute(self, dlq_urls: List[str]) -> Dict:
        """
        Processa eventos das DLQs
        
        Parâmetros:
            dlq_urls: Lista de URLs das filas DLQ a serem processadas
        
        Retorno:
            Dicionário com o resultado do processamento
        """
        results = {
            'processed': 0,
            'discarded': 0,
            'errors': []
        }
        
        for dlq_url in dlq_urls:
            try:
                # Obtém eventos da DLQ
                events = self.dlq_repository.get_events(dlq_url)
                
                for event in events:
                    try:
                        if event.has_exceeded_retries:
                            # Se excedeu o número de tentativas, descarta o evento
                            self.dlq_repository.delete_from_dlq(event)
                            results['discarded'] += 1
                        else:
                            # Move o evento para a fila original
                            self.dlq_repository.move_to_original_queue(event)
                            # Remove da DLQ após mover
                            self.dlq_repository.delete_from_dlq(event)
                            results['processed'] += 1
                    except Exception as e:
                        results['errors'].append({
                            'message_id': event.message_id,
                            'error': str(e)
                        })
            except Exception as e:
                results['errors'].append({
                    'queue_url': dlq_url,
                    'error': str(e)
                })
        
        return results 