from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class UserEntity:
    _id: str
    name: str
    createdAt: datetime = field(default_factory=datetime.now)
    lastActive: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self._validate_uuid(self._id)
    
    @property
    def id(self) -> str:
        return self._id
    
    @staticmethod
    def _validate_uuid(id_str: str) -> None:
        try:
            UUID(id_str)
        except ValueError:
            raise ValidationError(
                message=f"ID inválido: {id_str}. Debe ser un UUID válido.",
                code="INVALID_UUID",
                details={
                    "field": "id",
                    "value": id_str,
                    "expected": "UUID string"
                }
            )
    
    def update_last_active(self) -> None:
        self.lastActive = datetime.now()
