"""
Custom exception handler for Django REST Framework
Ensures all errors return JSON responses instead of HTML
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns JSON responses for all errors
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it means Django raised an exception
    # that DRF doesn't handle (like 400 Bad Request from Django itself)
    if response is None:
        # Check if it's a Django validation error
        if hasattr(exc, 'message_dict'):
            return Response(
                {
                    'error': 'Validation error',
                    'details': exc.message_dict,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif hasattr(exc, 'message'):
            return Response(
                {
                    'error': str(exc),
                    'details': exc.message if hasattr(exc, 'message') else str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Generic error handler
            logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)
            return Response(
                {
                    'error': 'An error occurred',
                    'details': str(exc) if str(exc) else f'{type(exc).__name__} occurred',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Customize the response data
    custom_response_data = {
        'error': 'An error occurred',
        'details': str(exc),
    }
    
    # If response already has data, use it
    if hasattr(response, 'data') and response.data:
        if isinstance(response.data, dict):
            custom_response_data = response.data
        else:
            custom_response_data['details'] = response.data
    
    response.data = custom_response_data
    
    return response

