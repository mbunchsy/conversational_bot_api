from abc import abstractmethod
from typing import Dict, Any
from .domain_error import DomainError

class InternalError(DomainError):    
    def error_type(self) -> str:
        return "INTERNAL_ERROR"
    
    def __init__(self, message: str = "Internal server error", code: str = None, details: dict = None):
        super().__init__(
            message=message,
            code=code or "INTERNAL_ERROR",
            status=500,
            details=details
        )
        