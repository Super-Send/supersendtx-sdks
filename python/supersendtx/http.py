from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from supersendtx.errors import SuperSendTXError


class HttpClient:
    def __init__(self, api_key: str, *, base_url: str = "https://api.supersendtx.com") -> None:
        if not api_key.startswith("stx_"):
            raise ValueError("SuperSend TX API key must start with stx_")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        payload = None
        req_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **(headers or {}),
        }
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(url, data=payload, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {}
            raise SuperSendTXError.from_response(error.code, parsed) from error

    @staticmethod
    def query(params: dict[str, Any]) -> str:
        filtered = {key: value for key, value in params.items() if value is not None}
        if not filtered:
            return ""
        return "?" + urllib.parse.urlencode(filtered)
