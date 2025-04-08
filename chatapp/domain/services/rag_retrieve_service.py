from abc import ABC, abstractmethod
from typing import List

class RAGRetrieveService(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]: 
        pass

    @abstractmethod
    def retrieve_context(self, query: str, k: int = 3) -> str:
        pass