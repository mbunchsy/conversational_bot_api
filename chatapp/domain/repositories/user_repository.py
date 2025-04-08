from abc import ABC, abstractmethod
from typing import Optional, List

from chatapp.domain.entities.user import UserEntity

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def save(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def create_anonymous(self) -> UserEntity:
        pass