import logging
import io

from typing import Callable, Iterable, Optional, Set
from urllib.parse import parse_qs


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
        """Processes the WSGI request and applies method override if necessary."""

        try:
            original_method = environ.get("REQUEST_METHOD", "GET")
            override_method = self._get_override_method(environ)

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

    def _get_override_method(self, environ: dict) -> Optional[str]:
        """Searches for the override method in headers or form data."""

        if self.header_override:
            headers = self._get_headers(environ)
            method = headers.get(self.header_override, "").strip().upper()
            if method:
                return method

        if environ.get("REQUEST_METHOD") == "POST":
            method = self._get_method_from_form(environ)
            if method:
                return method

        return None

    def _get_headers(self, environ: dict) -> dict:
        """Extract HTTP headers from the WSGI environ."""

        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-")
                headers[header_name] = value
        return headers

    def _get_method_from_form(self, environ: dict) -> Optional[str]:
        """Extracts the override method from the POST form."""

        try:
            input_stream = environ.get("wsgi.input")
            content_length = int(environ.get("CONTENT_LENGTH", 0))

            if not input_stream or content_length == 0:
                return None

            form_data = input_stream.read(content_length).decode("utf-8")
            environ["wsgi.input"] = io.BytesIO(form_data.encode())
            parsed_data = parse_qs(form_data)

            if self.override_param in parsed_data:
                method = parsed_data[self.override_param][0].strip().upper()
                return method if method else None
        except (ValueError, UnicodeDecodeError, IndexError):
            pass

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
