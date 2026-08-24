"""Django email backend for Ranla.

Send mapping lives in supersendtx.django; this wrapper uses the Ranla client
so the default host is api.ranla.ai and RANLA_API_KEY is read first.
"""

from __future__ import annotations

import os
from typing import Any

from ranla.client import DEFAULT_API_BASE_URL, Ranla
from supersendtx.django.email import EmailBackend as _TxEmailBackend

__all__ = ["EmailBackend"]


class EmailBackend(_TxEmailBackend):
    """
    Django email backend.

    EMAIL_BACKEND = "ranla.django.EmailBackend"
    """

    def __init__(
        self,
        fail_silently: bool = False,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        client: Ranla | None = None,
        **kwargs: Any,
    ) -> None:
        if client is not None:
            super().__init__(fail_silently=fail_silently, client=client, **kwargs)
            return
        key = api_key or os.environ.get("RANLA_API_KEY") or os.environ.get("SUPERSENDTX_API_KEY")
        if not key:
            raise ValueError("RANLA_API_KEY is not configured.")
        url = (
            base_url
            or os.environ.get("RANLA_BASE_URL")
            or os.environ.get("SUPERSENDTX_BASE_URL")
            or DEFAULT_API_BASE_URL
        )
        super().__init__(fail_silently=fail_silently, client=Ranla(key, base_url=url), **kwargs)
