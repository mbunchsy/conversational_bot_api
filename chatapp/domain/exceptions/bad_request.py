from chatapp.domain.exceptions.domain_error import DomainError

class BadRequestError(DomainError):   
    def error_code(self) -> str:
        return "BAD_REQUEST"

    def __init__(self, message: str = "No se puede procesar la solicitud", code: str = None, details: dict = None):
        super().__init__(
            message=message,
            code=code or "BAD_REQUEST",
            status=400,
            details=details
        )
