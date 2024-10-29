"""Tests for the Cloudflare Vectorize client."""

import pytest
from cloudflare_vectorize import CloudflareVectorize, CloudflareVectorizeError

def test_client_initialization():
    """Test client initialization with valid credentials."""
    client = CloudflareVectorize(
        "test-account-id",
        {"bearer_token": "test-token"}
    )
    assert client.headers["Authorization"] == "Bearer test-token"

def test_client_initialization_invalid():
    """Test client initialization with invalid credentials."""
    with pytest.raises(CloudflareVectorizeError):
        CloudflareVectorize("test-account-id", {}) 