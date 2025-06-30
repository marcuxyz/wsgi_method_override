"""
Unit tests for the Flask Method Override middleware.

This module contains comprehensive tests for the MethodOverrideMiddleware class
and the Flask application routes.
"""

import io
from src.wsgi_method_override.wsgi_method_override import (
    MethodOverrideMiddleware,
)


class TestMethodOverrideMiddleware:
    """Test cases for the MethodOverrideMiddleware class."""

    def test_init_with_defaults(self):
        """Test middleware initialization with default parameters."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        assert "GET" in middleware.allowed_methods
        assert "POST" in middleware.allowed_methods
        assert "PUT" in middleware.allowed_methods
        assert "PATCH" in middleware.allowed_methods
        assert "DELETE" in middleware.allowed_methods
        assert middleware.override_param == "_method"
        assert middleware.header_override == "X-HTTP-Method-Override"

    def test_init_with_custom_parameters(self):
        """Test middleware initialization with custom parameters."""

        def dummy_app(environ, start_response):
            return []

        custom_methods = ["GET", "POST", "PUT"]
        custom_bodyless = ["GET"]

        middleware = MethodOverrideMiddleware(
            dummy_app,
            allowed_methods=custom_methods,
            bodyless_methods=custom_bodyless,
            override_param="custom_method",
            header_override="Custom-Method",
        )

        assert middleware.allowed_methods == frozenset(["GET", "POST", "PUT"])
        assert middleware.bodyless_methods == frozenset(["GET"])
        assert middleware.override_param == "custom_method"
        assert middleware.header_override == "Custom-Method"

    def test_is_override_allowed_success(self):
        """Test successful method override validation."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Should allow POST to PATCH override
        assert middleware._is_override_allowed("POST", "PATCH") is True

        # Should allow POST to PUT override
        assert middleware._is_override_allowed("POST", "PUT") is True

        # Should allow POST to DELETE override
        assert middleware._is_override_allowed("POST", "DELETE") is True

    def test_is_override_allowed_failure(self):
        """Test method override validation failures."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Should not allow GET to PATCH override
        assert middleware._is_override_allowed("GET", "PATCH") is False

        # Should not allow POST to POST override
        assert middleware._is_override_allowed("POST", "POST") is False

        # Should not allow POST to invalid method
        assert middleware._is_override_allowed("POST", "INVALID") is False

    def test_get_headers_success(self):
        """Test successful header extraction from WSGI environ."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Test environ with HTTP headers
        environ = {
            "HTTP_X_HTTP_METHOD_OVERRIDE": "PUT",
            "HTTP_CONTENT_TYPE": "application/json",
            "HTTP_USER_AGENT": "TestAgent/1.0",
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/test",
        }

        headers = middleware._get_headers(environ)

        assert headers["X-HTTP-METHOD-OVERRIDE"] == "PUT"
        assert headers["CONTENT-TYPE"] == "application/json"
        assert headers["USER-AGENT"] == "TestAgent/1.0"

    def test_get_headers_empty(self):
        """Test header extraction with no HTTP headers."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Test environ without HTTP headers
        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/test",
            "CONTENT_LENGTH": "10",
        }

        headers = middleware._get_headers(environ)

        assert headers == {}

    def test_get_headers_mixed_environ(self):
        """Test header extraction with mixed environ variables."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Test environ with mixed HTTP and non-HTTP variables
        environ = {
            "HTTP_ACCEPT": "text/html",
            "HTTP_CUSTOM_HEADER": "custom-value",
            "REQUEST_METHOD": "POST",
            "CONTENT_LENGTH": "10",
            "PATH_INFO": "/test",
        }

        headers = middleware._get_headers(environ)

        assert headers["ACCEPT"] == "text/html"
        assert headers["CUSTOM-HEADER"] == "custom-value"
        assert len(headers) == 2  # Only HTTP_ prefixed variables

    def test_get_method_from_form_success(self):
        """Test successful method extraction from form data."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Create form data
        form_data = "_method=PUT&name=test&email=test@example.com"
        form_bytes = form_data.encode("utf-8")

        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.BytesIO(form_bytes),
            "CONTENT_LENGTH": str(len(form_bytes)),
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
        }

        method = middleware._get_method_from_form(environ)

        assert method == "PUT"
        # Verify stream was reset for application to read
        environ["wsgi.input"].seek(0)
        assert environ["wsgi.input"].read().decode("utf-8") == form_data

    def test_get_method_from_form_custom_param(self):
        """Test method extraction with custom parameter name."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(
            dummy_app, override_param="custom_method"
        )

        # Create form data with custom parameter
        form_data = "custom_method=PATCH&data=value"
        form_bytes = form_data.encode("utf-8")

        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.BytesIO(form_bytes),
            "CONTENT_LENGTH": str(len(form_bytes)),
        }

        method = middleware._get_method_from_form(environ)

        assert method == "PATCH"

    def test_get_method_from_form_no_override_param(self):
        """Test form parsing when override parameter is not present."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Create form data without _method parameter
        form_data = "name=test&email=test@example.com"
        form_bytes = form_data.encode("utf-8")

        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.BytesIO(form_bytes),
            "CONTENT_LENGTH": str(len(form_bytes)),
        }

        method = middleware._get_method_from_form(environ)

        assert method is None

    def test_get_method_from_form_empty_content(self):
        """Test form parsing with empty content."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.BytesIO(b""),
            "CONTENT_LENGTH": "0",
        }

        method = middleware._get_method_from_form(environ)

        assert method is None

    def test_get_method_from_form_no_input_stream(self):
        """Test form parsing when input stream is missing."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        environ = {"REQUEST_METHOD": "POST", "CONTENT_LENGTH": "10"}

        method = middleware._get_method_from_form(environ)

        assert method is None

    def test_get_method_from_form_invalid_encoding(self):
        """Test form parsing with invalid UTF-8 encoding."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Create invalid UTF-8 bytes
        invalid_bytes = b"\xff\xfe_method=PUT"

        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.BytesIO(invalid_bytes),
            "CONTENT_LENGTH": str(len(invalid_bytes)),
        }

        method = middleware._get_method_from_form(environ)

        # Should return None and handle error gracefully
        assert method is None

    def test_get_method_from_form_empty_method_value(self):
        """Test form parsing when method parameter has empty value."""

        def dummy_app(environ, start_response):
            return []

        middleware = MethodOverrideMiddleware(dummy_app)

        # Create form data with empty _method value
        form_data = "_method=&name=test"
        form_bytes = form_data.encode("utf-8")

        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.BytesIO(form_bytes),
            "CONTENT_LENGTH": str(len(form_bytes)),
        }

        method = middleware._get_method_from_form(environ)

        assert method is None
