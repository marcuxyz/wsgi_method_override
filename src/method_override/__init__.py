"""
Method Override Middleware for WSGI Applications.

This package provides a WSGI middleware that enables HTTP method override
functionality for web applications, allowing HTML forms to use methods
other than GET and POST.
"""

from .wsgi_method_override import MethodOverrideMiddleware

__version__ = "0.3.0"
__all__ = ["MethodOverrideMiddleware"]
