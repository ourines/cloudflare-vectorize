"""
Cloudflare Vectorize API Python Client

A Python client for interacting with Cloudflare's Vectorize API.
"""

from .client import CloudflareVectorize
from .exceptions import CloudflareVectorizeError

__version__ = "0.1.2"
__all__ = ["CloudflareVectorize", "CloudflareVectorizeError"] 