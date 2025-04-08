from .domain_error import DomainError

class ValidationError(DomainError):    
    def error_type(self) -> str:
        return "VALIDATION"
    
    def __init__(self, message: str = "Validation error", code: str = None, details: dict = None):
        super().__init__(
            message=message,
            code=code or "VALIDATION_ERROR",
            status=400,
            details=details
        )
        