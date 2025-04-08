import uuid
from django.db import models
from chatapp.domain.entities.user import UserEntity

class UserDB(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def to_entity(self) -> UserEntity:
        return UserEntity(
            _id=str(self.id),
            name=self.name
        )

    @classmethod
    def from_entity(cls, entity: UserEntity) -> 'UserDB':
        return cls(
            id=uuid.UUID(entity.id) if isinstance(entity.id, str) else entity.id,
            name=entity.name
        )