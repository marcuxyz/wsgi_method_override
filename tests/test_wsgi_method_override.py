"""
Unit tests for the Flask Method Override middleware.

This module contains comprehensive tests for the MethodOverrideMiddleware class
and the Flask application routes.
"""

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
