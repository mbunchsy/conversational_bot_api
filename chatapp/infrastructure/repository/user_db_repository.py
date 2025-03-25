from typing import Optional
from django.core.exceptions import ObjectDoesNotExist
from uuid import uuid4

from chatapp.domain.entities.user import UserEntity
from chatapp.domain.repositories.user_repository import UserRepository
from chatapp.infrastructure.models.user_db import UserDB

class UserDBRepository(UserRepository):
    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        try:
            user_db = UserDB.objects.get(id=user_id)
            return user_db.to_entity()
        except ObjectDoesNotExist:
            return None

    def save(self, user: UserEntity) -> UserEntity:
        user_db = UserDB.from_entity(user)
        user_db.save()
        return user_db.to_entity()

    def create_anonymous(self) -> UserEntity:
        user_id = str(uuid4())
        user = UserEntity(
            _id=user_id,
            name=f"Anonymous_{user_id[:8]}",
        )
        return self.save(user)