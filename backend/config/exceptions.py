import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': response.data,
            }
        }
    else:
        # Log the actual exception for debugging
        logger.exception(f"Unhandled exception: {exc}")
        # Return generic error message to avoid leaking internal details
        response = Response({
            'success': False,
            'error': {
                'status_code': 500,
                'message': 'An internal server error occurred. Please try again later.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response
