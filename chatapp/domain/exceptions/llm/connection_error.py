from chatapp.domain.exceptions.validation_error import ValidationError

class LLMConnectionError(ValidationError):
    def __init__(self, message: str = "Error de conexión con el servicio LLM", details: dict = None):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            details=details
        )