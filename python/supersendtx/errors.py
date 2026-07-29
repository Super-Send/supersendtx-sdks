from __future__ import annotations

from typing import Any


class SuperSendTXError(Exception):
    def __init__(
        self,
        message: str,
        status: int,
        *,
        details: Any = None,
        code: str | None = None,
        upgrade_url: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.details = details
        self.code = code
        self.upgrade_url = upgrade_url

    @classmethod
    def from_response(cls, status: int, body: Any) -> SuperSendTXError:
        err = body.get("error") if isinstance(body, dict) else None
        if isinstance(err, str):
            message = err
            details = None
            code = None
            upgrade_url = None
        elif isinstance(err, dict):
            message = str(err.get("message") or f"Request failed with status {status}")
            details = err.get("details")
            code = str(err["code"]) if err.get("code") is not None else None
            upgrade_url = str(err["upgrade_url"]) if err.get("upgrade_url") is not None else None
        else:
            message = f"Request failed with status {status}"
            details = None
            code = None
            upgrade_url = None
        return cls(message, status, details=details, code=code, upgrade_url=upgrade_url)
