"""SuperSend TX Python SDK — transactional email API client."""

from supersendtx.client import SuperSendTX
from supersendtx.errors import SuperSendTXError

__all__ = ["SuperSendTX", "SuperSendTXError"]
DEFAULT_API_BASE_URL = "https://api.supersendtx.com"
