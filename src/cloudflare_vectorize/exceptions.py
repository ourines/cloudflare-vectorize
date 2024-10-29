"""Exceptions for the Cloudflare Vectorize client."""

class CloudflareVectorizeError(Exception):
    """Base exception for Cloudflare Vectorize errors."""
    pass

class AuthenticationError(CloudflareVectorizeError):
    """Raised when authentication fails."""
    pass

class APIError(CloudflareVectorizeError):
    """Raised when the API returns an error."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or [] 