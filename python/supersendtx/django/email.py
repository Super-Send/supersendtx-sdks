from __future__ import annotations

import base64
import os
from email.utils import parseaddr
from typing import Any

from supersendtx.client import SuperSendTX
from supersendtx.errors import SuperSendTXError

HEADER_IDEMPOTENCY = "X-SuperSendTX-Idempotency-Key"
HEADER_SCHEDULED_AT = "X-SuperSendTX-Scheduled-At"
HEADER_TAG = "X-SuperSendTX-Tag"

RESERVED_HEADERS = {
    "from",
    "to",
    "cc",
    "bcc",
    "reply-to",
    "subject",
    "content-type",
    "mime-version",
    "date",
    "message-id",
    HEADER_IDEMPOTENCY.lower(),
    HEADER_SCHEDULED_AT.lower(),
    HEADER_TAG.lower(),
    "idempotency-key",
}

try:
    from django.core.mail.backends.base import BaseEmailBackend as _BaseEmailBackend
except ImportError:  # pragma: no cover
    _BaseEmailBackend = object  # type: ignore[misc, assignment]


def _format_address(value: str) -> str:
    name, email = parseaddr(value)
    email = email.strip()
    name = name.strip()
    if not email:
        return value.strip()
    return f"{name} <{email}>" if name else email


def _address_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [_format_address(str(v)) for v in value if str(v).strip()]
    return [_format_address(str(value))]


def _parse_tag(text_value: str) -> dict[str, str] | None:
    trimmed = text_value.strip()
    if not trimmed:
        return None
    if "=" in trimmed:
        name, tag_value = trimmed.split("=", 1)
        if name.strip() and tag_value.strip():
            return {"name": name.strip(), "value": tag_value.strip()}
        return None
    return {"name": "tag", "value": trimmed}


def email_message_to_send_params(message: Any) -> dict[str, Any]:
    from_list = _address_list(message.from_email)
    if not from_list:
        raise ValueError("Email is missing a From address.")
    to = _address_list(message.to)
    if not to:
        raise ValueError("Email is missing a To recipient.")

    html: str | None = None
    text: str | None = None
    if hasattr(message, "alternatives"):
        for content, mimetype in message.alternatives or []:
            if mimetype == "text/html" and content:
                html = str(content)
    body = getattr(message, "body", None)
    content_subtype = getattr(message, "content_subtype", "plain")
    if body:
        if content_subtype == "html" and html is None:
            html = str(body)
        elif content_subtype != "html":
            text = str(body)

    if not html and not text:
        raise ValueError("Email must include html or text content.")

    params: dict[str, Any] = {
        "from": from_list[0],
        "to": to[0] if len(to) == 1 else to,
    }
    if message.subject:
        params["subject"] = message.subject
    if html:
        params["html"] = html
    if text:
        params["text"] = text

    cc = _address_list(getattr(message, "cc", None))
    if cc:
        params["cc"] = cc
    bcc = _address_list(getattr(message, "bcc", None))
    if bcc:
        params["bcc"] = bcc
    reply_to = _address_list(getattr(message, "reply_to", None))
    if reply_to:
        params["reply_to"] = reply_to[0] if len(reply_to) == 1 else reply_to

    attachments = []
    for attachment in getattr(message, "attachments", []) or []:
        if isinstance(attachment, tuple) and len(attachment) >= 2:
            filename, content = attachment[0], attachment[1]
            mimetype = attachment[2] if len(attachment) > 2 else "application/octet-stream"
            raw = content.encode("utf-8") if isinstance(content, str) else bytes(content)
            attachments.append(
                {
                    "filename": filename or "attachment",
                    "content_type": mimetype or "application/octet-stream",
                    "content": base64.b64encode(raw).decode("ascii"),
                }
            )
    if attachments:
        params["attachments"] = attachments

    extra_headers = getattr(message, "extra_headers", None) or {}
    tags: list[dict[str, str]] = []
    forward: dict[str, str] = {}
    idempotency_key: str | None = None
    scheduled_at: str | None = None

    for key, value in extra_headers.items():
        lower = str(key).lower()
        if lower == HEADER_TAG.lower():
            values = value if isinstance(value, list) else [value]
            for item in values:
                tag = _parse_tag(str(item))
                if tag:
                    tags.append(tag)
            continue

        text_value = str(value).strip()
        if not text_value:
            continue
        if lower in {HEADER_IDEMPOTENCY.lower(), "idempotency-key"}:
            idempotency_key = text_value
            continue
        if lower == HEADER_SCHEDULED_AT.lower():
            scheduled_at = text_value
            continue
        if lower in RESERVED_HEADERS or lower.startswith("content-"):
            continue
        forward[str(key)] = text_value

    if tags:
        params["tags"] = tags
    if forward:
        params["headers"] = forward
    if idempotency_key:
        params["idempotency_key"] = idempotency_key
    if scheduled_at:
        params["scheduled_at"] = scheduled_at

    return params


class EmailBackend(_BaseEmailBackend):  # type: ignore[misc, valid-type]
    """
    Django email backend.

    EMAIL_BACKEND = "supersendtx.django.EmailBackend"
    """

    def __init__(
        self,
        fail_silently: bool = False,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        client: SuperSendTX | None = None,
        **kwargs: Any,
    ) -> None:
        if _BaseEmailBackend is object:  # pragma: no cover
            raise ImportError(
                "Django is required for supersendtx.django.EmailBackend. "
                "Install with: pip install 'supersendtx[django]'"
            )
        super().__init__(fail_silently=fail_silently)
        if client is not None:
            self._client = client
        else:
            key = api_key or os.environ.get("SUPERSENDTX_API_KEY")
            if not key:
                raise ValueError("SUPERSENDTX_API_KEY is not configured.")
            url = base_url or os.environ.get("SUPERSENDTX_BASE_URL")
            self._client = SuperSendTX(key, base_url=url) if url else SuperSendTX(key)

    def send_messages(self, email_messages: list[Any]) -> int:
        if not email_messages:
            return 0
        sent = 0
        for message in email_messages:
            try:
                params = email_message_to_send_params(message)
                # emails.send uses from_ keyword; map "from" key
                from_addr = params.pop("from")
                self._client.emails.send(from_=from_addr, **params)
                sent += 1
            except (SuperSendTXError, ValueError, TypeError):
                if not self.fail_silently:
                    raise
        return sent
