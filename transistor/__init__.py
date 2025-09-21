"""
Transistor.fm API Python Client

A complete Python client library for the Transistor.fm podcast hosting API.
Provides full access to shows, episodes, analytics, subscribers, and file uploads.

Example:
    >>> from transistor import TransistorClient
    >>> client = TransistorClient('your_api_key')
    >>> account = client.get_account()
    >>> shows = client.list_shows()
"""

from .client import TransistorClient
from .exceptions import (
    TransistorAPIError,
    RateLimitError, 
    AuthenticationError,
    NotFoundError,
    ValidationError
)

__version__ = "1.0.0"
__author__ = "Amazon Q Developer"
__email__ = "support@example.com"
__license__ = "MIT"

__all__ = [
    "TransistorClient",
    "TransistorAPIError", 
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError", 
    "ValidationError"
]
