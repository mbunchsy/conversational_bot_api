from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DomainError(Exception, ABC):    
    def __init__(self, message: str, code: str = None, status: int = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.status = status
        self.details = details or {}
        super().__init__(self.message)
        
        logger.error(f"{self.status} - {self.code}: {self.message}", extra={"details": self.details})
    
    @abstractmethod
    def error_type(self) -> str:
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.error_type(),
            "code": self.code,
            "status": self.status,
            "message": self.message,
            "details": self.details
        }