"""
Transistor.fm API Exception Classes

Custom exceptions for handling different types of API errors with appropriate
status codes and response information.
"""


class TransistorAPIError(Exception):
    """
    Base exception for all Transistor API errors
    
    Attributes:
        message (str): Error message
        status_code (int): HTTP status code (if available)
        response: Raw HTTP response object (if available)
    """
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(TransistorAPIError):
    """
    Raised when API rate limit is exceeded (HTTP 429)
    
    The Transistor API is limited to 10 requests per 10 seconds.
    When this limit is exceeded, wait 10 seconds before retrying.
    """
    pass


class AuthenticationError(TransistorAPIError):
    """
    Raised when API authentication fails (HTTP 401)
    
    This typically indicates an invalid or missing API key.
    Check your API key at dashboard.transistor.fm/account
    """
    pass


class NotFoundError(TransistorAPIError):
    """
    Raised when a requested resource is not found (HTTP 404)
    
    This can occur when:
    - The resource ID doesn't exist
    - You don't have access to the resource
    - The endpoint URL is incorrect
    """
    pass


class ValidationError(TransistorAPIError):
    """
    Raised when request validation fails (HTTP 422)
    
    This occurs when the request data doesn't meet the API's
    validation requirements (missing fields, invalid formats, etc.)
    """
    pass
