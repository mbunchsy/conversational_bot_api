from ..forbidden_error import ForbiddenError

class LLMAuthenticationError(ForbiddenError):
    """Error for LLM authentication issues"""
    
    def __init__(self, message: str = "Error de autenticación con el servicio LLM", details: dict = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details=details
        )