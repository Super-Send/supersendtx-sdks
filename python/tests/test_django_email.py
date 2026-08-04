from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from supersendtx.django.email import HEADER_IDEMPOTENCY, HEADER_TAG, email_message_to_send_params
from supersendtx.django import EmailBackend


def test_email_message_to_send_params_maps_fields() -> None:
    message = SimpleNamespace(
        from_email="Ops <ops@example.com>",
        to=["user@example.com"],
        cc=["cc@example.com"],
        bcc=[],
        reply_to=["reply@example.com"],
        subject="Hello",
        body="Hi",
        content_subtype="plain",
        alternatives=[("<p>Hi</p>", "text/html")],
        attachments=[("note.txt", b"hello", "text/plain")],
        extra_headers={
            HEADER_TAG: ["campaign=welcome", "env=prod"],
            HEADER_IDEMPOTENCY: "idem-django",
            "X-Custom-Header": "keep",
        },
    )

    params = email_message_to_send_params(message)
    assert params["from"] == "Ops <ops@example.com>"
    assert params["to"] == "user@example.com"
    assert params["html"] == "<p>Hi</p>"
    assert params["text"] == "Hi"
    assert params["tags"] == [
        {"name": "campaign", "value": "welcome"},
        {"name": "env", "value": "prod"},
    ]
    assert params["idempotency_key"] == "idem-django"
    assert params["headers"] == {"X-Custom-Header": "keep"}
    assert params["attachments"][0]["filename"] == "note.txt"


def test_email_backend_send_messages() -> None:
    django = pytest.importorskip("django")
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            EMAIL_BACKEND="supersendtx.django.EmailBackend",
            SECRET_KEY="test",
            USE_I18N=False,
        )
    django.setup()

    from django.core.mail import EmailMultiAlternatives

    client = MagicMock()
    client.emails.send.return_value = {"id": "msg_1", "status": "queued"}
    backend = EmailBackend(client=client)

    message = EmailMultiAlternatives(
        subject="Hello",
        body="Hi",
        from_email="ops@example.com",
        to=["user@example.com"],
    )
    message.attach_alternative("<p>Hi</p>", "text/html")
    message.extra_headers[HEADER_TAG] = "campaign=welcome"

    assert backend.send_messages([message]) == 1
    client.emails.send.assert_called_once()
    kwargs = client.emails.send.call_args.kwargs
    assert kwargs["from_"] == "ops@example.com"
    assert kwargs["to"] == "user@example.com"
    assert kwargs["html"] == "<p>Hi</p>"
