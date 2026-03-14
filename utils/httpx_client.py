"""
Shared HTTPX Client for HTTP requests
Connection pooling for better performance
"""
import httpx

# Shared httpx client with connection pooling
_client = None


def get_httpx_client() -> httpx.Client:
    """
    Get or create a shared httpx client with connection pooling.
    This improves performance by reusing connections.
    """
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        )
    return _client


def close_httpx_client():
    """Close the shared httpx client"""
    global _client
    if _client is not None:
        _client.close()
        _client = None
