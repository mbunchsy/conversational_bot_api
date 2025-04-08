from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from chatapp.domain.exceptions.domain_error import DomainError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None or not isinstance(exc, DomainError):
        return response
    
    error_dict = exc.to_dict()
    
    return Response(
        {"error": error_dict},
        status=error_dict.get("status", status.HTTP_500_INTERNAL_SERVER_ERROR)
    )