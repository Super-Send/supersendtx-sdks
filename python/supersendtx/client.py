from __future__ import annotations

from typing import Any

from supersendtx.errors import SuperSendTXError
from supersendtx.http import HttpClient
from supersendtx.resources import (
    DomainsResource,
    EmailsResource,
    SuppressionsResource,
    TemplatesResource,
    WebhooksResource,
)

DEFAULT_API_BASE_URL = "https://api.supersendtx.com"


class SuperSendTX:
    """Thin HTTP client for the SuperSend TX REST API."""

    def __init__(self, api_key: str, *, base_url: str = DEFAULT_API_BASE_URL) -> None:
        self._http = HttpClient(api_key, base_url=base_url)
        self.emails = EmailsResource(self._http)
        self.domains = DomainsResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.templates = TemplatesResource(self._http)
        self.suppressions = SuppressionsResource(self._http)

    def request(self, method: str, path: str, *, body: Any = None, headers: dict[str, str] | None = None) -> Any:
        return self._http.request(method, path, body=body, headers=headers)
