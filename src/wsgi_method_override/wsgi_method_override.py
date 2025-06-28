import logging
from typing import Callable, Iterable, Optional, Set

from werkzeug.wrappers import Request


class MethodOverrideMiddleware:
    """
    WSGI middleware that allows HTTP method override via form parameter.

    This middleware enables HTML forms to use HTTP methods other than GET and POST
    by checking for a '_method' parameter in the request data.

    Args:
        app: The WSGI application to wrap
        allowed_methods: Set of HTTP methods that can be overridden
        bodyless_methods: Set of HTTP methods that should not have a body
        override_param: Name of the form parameter used for method override
        header_override: Name of the header used for method override (optional)
    """

    DEFAULT_ALLOWED_METHODS: Set[str] = frozenset(
        {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
    )

    DEFAULT_BODYLESS_METHODS: Set[str] = frozenset(
        {"GET", "HEAD", "OPTIONS", "DELETE"}
    )

    def __init__(
        self,
        app: Callable,
        allowed_methods: Optional[Iterable[str]] = None,
        bodyless_methods: Optional[Iterable[str]] = None,
        override_param: str = "_method",
        header_override: Optional[str] = "X-HTTP-Method-Override",
    ) -> None:
        """Initialize the middleware with configuration options."""

        self.app = app
        self.allowed_methods = frozenset(
            method.upper()
            for method in (allowed_methods or self.DEFAULT_ALLOWED_METHODS)
        )
        self.bodyless_methods = frozenset(
            method.upper()
            for method in (bodyless_methods or self.DEFAULT_BODYLESS_METHODS)
        )
        self.override_param = override_param
        self.header_override = header_override
        self.logger = logging.getLogger(__name__)

        self.logger.info(
            f"MethodOverrideMiddleware initialized with allowed methods: {self.allowed_methods}"
        )

    def __call__(self, environ: dict, start_response: Callable) -> Iterable:
        """Process the WSGI request and apply method override if applicable."""

        try:
            request = Request(environ)
            original_method = environ.get("REQUEST_METHOD", "GET")
            override_method = self._get_override_method(request)

            if override_method and self._is_override_allowed(
                original_method, override_method
            ):
                self.logger.debug(
                    f"Overriding method from {original_method} to {override_method}"
                )
                environ["REQUEST_METHOD"] = override_method

                if override_method in self.bodyless_methods:
                    environ["CONTENT_LENGTH"] = "0"
                    environ.pop("CONTENT_TYPE", None)

        except Exception as e:
            self.logger.error(f"Error in MethodOverrideMiddleware: {e}")

        return self.app(environ, start_response)

    def _get_override_method(self, request: Request) -> Optional[str]:
        """Extract the override method from request parameters or headers."""

        if self.override_param in request.form:
            method = request.form.get(self.override_param, "").strip().upper()
            if method:
                return method

        if self.header_override:
            method = (
                request.headers.get(self.header_override, "").strip().upper()
            )
            if method:
                return method

        return None

    def _is_override_allowed(
        self, original_method: str, override_method: str
    ) -> bool:
        """Check if the method override is allowed based on security rules."""

        if original_method != "POST":
            self.logger.warning(
                f"Method override attempted from {original_method}, only POST is allowed"
            )
            return False

        if override_method not in self.allowed_methods:
            self.logger.warning(
                f"Method override to {override_method} not allowed"
            )
            return False

        if original_method == override_method:
            return False

        return True
