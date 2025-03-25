from chatapp.domain.exceptions.internal_error import InternalError

class LLMGenericError(InternalError):    
    def __init__(self, message: str = "Error inesperado al procesar el mensaje", details: dict = None):
        super().__init__(
            message=message,
            code="GENERIC_ERROR",
            details=details
        )