"""
Rate limiting configuration.

This module configures the rate limiter for the application
using the client's remote address as the key function.

:author: Artur
:version: 1.0.0
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
