# Method Override Middleware

A Python WSGI middleware that allows HTTP method override via form parameters or headers. This enables HTML forms to use HTTP methods other than GET and POST by providing a method override mechanism.

## Features

- 🔄 Override HTTP methods via form parameters (`_method`) or custom headers
- 🛡️ Security-focused: Only allows overrides from POST requests
- 🎯 Configurable allowed methods and parameters
- 📝 Comprehensive logging for debugging and monitoring
- 🚀 Compatible with any WSGI application (Flask). Coming soon Django, FastAPI and etc
- ⚡ Zero dependencies - uses only Python standard library

## Installation

Install using pip:

```bash
pip install method-override
```

Or using Poetry:

```bash
poetry add method-override
```

## Quick Start

### Basic Usage

```python
from method_override import MethodOverrideMiddleware

# Wrap your WSGI application
app = MethodOverrideMiddleware(your_wsgi_app)
```

### Flask Example

```python
from flask import Flask
from method_override import MethodOverrideMiddleware

app = Flask(__name__)

# Apply the middleware
app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)

@app.put('/users/<int:user_id>')
def edit_user(user_id):
    return f"Updating user {user_id}"

@app.delete('/users/<int:user_id>')
def delete_user(user_id):
    return f"Deleting user {user_id}"
```

### HTML Form Usage

```html
<!-- HTML forms can now use PUT, PATCH, DELETE methods -->
<form method="POST" action="/users/123">
    <input type="hidden" name="_method" value="PUT">
    <input type="text" name="name" placeholder="User name">
    <button type="submit">Update User</button>
</form>

<form method="POST" action="/users/123">
    <input type="hidden" name="_method" value="DELETE">
    <button type="submit">Delete User</button>
</form>
```

### AJAX/Header Usage

```javascript
// You can also use the X-HTTP-Method-Override header
fetch('/users/123', {
    method: 'POST',
    headers: {
        'X-HTTP-Method-Override': 'PUT',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name: 'John Doe' })
});
```

## Configuration

### Advanced Configuration

```python
from method_override import MethodOverrideMiddleware

app = MethodOverrideMiddleware(
    your_wsgi_app,
    allowed_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],  # Allowed override methods
    bodyless_methods=['GET', 'HEAD', 'OPTIONS', 'DELETE'],      # Methods without body
    override_param='_method',                                   # Form parameter name
    header_override='X-HTTP-Method-Override'                    # Header name for override
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allowed_methods` | `Iterable[str]` | `['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']` | HTTP methods that can be used as overrides |
| `bodyless_methods` | `Iterable[str]` | `['GET', 'HEAD', 'OPTIONS', 'DELETE']` | Methods that should not have a request body |
| `override_param` | `str` | `'_method'` | Form parameter name used for method override |
| `header_override` | `str` | `'X-HTTP-Method-Override'` | HTTP header name for method override |

## Security

This middleware implements several security measures:

- **POST-only overrides**: Method override is only allowed from POST requests
- **Whitelist approach**: Only explicitly allowed methods can be used as overrides
- **No self-override**: Cannot override a method to itself
- **Body handling**: Automatically removes body content for bodyless methods

## How It Works

1. The middleware intercepts incoming WSGI requests
2. Checks if the original request method is POST
3. Looks for override method in:
   - HTTP headers (`X-HTTP-Method-Override` by default) - checked first for performance
   - Form data (`_method` parameter by default) - only for POST requests
4. Validates the override method against allowed methods
5. Updates the `REQUEST_METHOD` in the WSGI environ
6. Handles body content appropriately for bodyless methods

### Technical Implementation

The middleware uses a clean, zero-dependency approach:

- **Direct WSGI environ manipulation**: No external dependencies required
- **Stream handling**: Carefully reads and reconstructs the request body stream to avoid conflicts
- **Header parsing**: Efficiently extracts HTTP headers from WSGI environ variables
- **Form parsing**: Uses Python's built-in `urllib.parse.parse_qs` for form data processing
- **Error resilience**: Gracefully handles malformed requests without breaking the application

## Use Cases

- **RESTful APIs**: Enable full REST verb support in HTML forms
- **Legacy browser support**: Support for older browsers that only support GET/POST
- **Form-based applications**: Build rich web applications with proper HTTP semantics
- **API consistency**: Maintain consistent API design across different client types

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/marcuxyz/method-override.git
cd method-override

# Install dependencies
poetry install
```

### Running Tests

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/wsgi_method_override
```

### Code Formatting

```bash
# Format code
poetry run black .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.3.0
- **📦 Better Package Name**: Renamed from `wsgi-method-override` to `method-override` for better discoverability

### v0.2.1
- **🚀 Zero Dependencies**: Completely removed Werkzeug dependency - now uses only Python standard library
- **🧹 Code Simplification**: Major refactor for better readability and maintainability
- **🐛 Bug Fix**: Resolved browser hanging issue when accessing `request.form` in WSGI applications
- **⚡ Performance**: Faster form parsing with direct stream handling
- **📖 Better Documentation**: Improved code comments and documentation in Portuguese for better understanding
- **🔧 Improved Error Handling**: More robust error handling with graceful fallbacks
- **🎯 Cleaner API**: Simplified internal methods with clear, descriptive names
- **💡 Better Debugging**: Enhanced logging for troubleshooting middleware issues

### v0.2.0
- **Python Compatibility**: Expanded Python version support from 3.12.4 to >=3.10.0
- **Broader Compatibility**: Now supports Python 3.10, 3.11, and 3.12+
- **Improved Accessibility**: Makes the package available to more users with different Python versions

### v0.1.0
- Initial release
- Basic method override functionality
- Support for form parameters and headers
- Comprehensive test suite
- Security measures implemented

## Support

If you encounter any issues or have questions, please:

1. Check the [documentation](https://github.com/marcuxyz/method-override)
2. Search existing [issues](https://github.com/marcuxyz/method-override/issues)
3. Create a new issue if needed

## Authors

- **Marcus Almeida** - *Initial work* - [marcuxyz](https://github.com/marcuxyz)

## Acknowledgments

- Inspired by similar middleware implementations in other web frameworks
- Built with Python standard library for maximum compatibility
- Follows WSGI standards and best practices
