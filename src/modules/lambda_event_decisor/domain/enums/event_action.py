from enum import Enum, auto

class EventAction(Enum):
    """
    Enum que representa as possíveis ações para um evento
    """
    UPSERT = auto()
    DROP = auto()
    NO_ACTION = auto()
    
    def __str__(self) -> str:
        return self.name.lower() 