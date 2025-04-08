from chatapp.domain.exceptions.internal_error import InternalError

class LLMRateLimitError(InternalError):    
    def __init__(self, message: str = "Rate limit exceeded for LLM service", details: dict = None):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            details=details
        )
        