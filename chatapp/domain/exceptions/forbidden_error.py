from .domain_error import DomainError

class ForbiddenError(DomainError):    
    def error_type(self) -> str:
        return "FORBIDDEN_ERROR"
    
    def __init__(self, message: str = "forbidden access", code: str = None, details: dict = None):
        super().__init__(
            message=message,
            code=code or "FORBIDDEN_ERROR",
            status=404,
            details=details
        )