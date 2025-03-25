
from .domain_error import DomainError

class NotFoundError(DomainError):    
    def error_type(self) -> str:
        return "NOT_FOUND"
    
    def __init__(self, message: str = "Recurso no encontrado", code: str = None, details: dict = None):
        super().__init__(
            message=message,
            code=code or "NOT_FOUND_ERROR",
            status=404,
            details=details
        )