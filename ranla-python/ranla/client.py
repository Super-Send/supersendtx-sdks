from __future__ import annotations

from supersendtx.client import SuperSendTX as _SuperSendTX

DEFAULT_API_BASE_URL = "https://api.ranla.ai"


class SuperSendTX(_SuperSendTX):
    """Ranla client — same API as supersendtx with Ranla default host."""

    def __init__(self, api_key: str, *, base_url: str = DEFAULT_API_BASE_URL) -> None:
        super().__init__(api_key, base_url=base_url)


Ranla = SuperSendTX
