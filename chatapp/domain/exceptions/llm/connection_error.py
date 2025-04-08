from chatapp.domain.exceptions.validation_error import ValidationError

class LLMConnectionError(ValidationError):
    def __init__(self, message: str = "Connection error with LLM service", details: dict = None):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            details=details
        )
        