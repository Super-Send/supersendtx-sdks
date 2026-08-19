from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from ranla import DEFAULT_API_BASE_URL, Ranla, SuperSendTX
from supersendtx.errors import SuperSendTXError


def test_default_host_is_ranla() -> None:
    assert DEFAULT_API_BASE_URL == "https://api.ranla.ai"
    client = Ranla("rnl_test_key")
    assert client._http.base_url == DEFAULT_API_BASE_URL


def test_super_send_tx_alias() -> None:
    assert SuperSendTX is Ranla


def test_requires_key_prefix() -> None:
    with pytest.raises(ValueError, match="stx_ or rnl_"):
        Ranla("bad")


def test_emails_send_uses_ranla_host() -> None:
    response = MagicMock()
    response.read.return_value = json.dumps({"id": "msg_1", "status": "sent"}).encode()
    response.__enter__.return_value = response

    client = Ranla("rnl_test_key")

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        result = client.emails.send(
            from_="a@example.com",
            to="b@example.com",
            subject="Hi",
            html="<p>Hi</p>",
        )

    assert result == {"id": "msg_1", "status": "sent"}
    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.ranla.ai/emails"
    assert request.get_header("Authorization") == "Bearer rnl_test_key"


def test_base_url_override() -> None:
    client = Ranla("rnl_test_key", base_url="https://api.example.com")
    assert client._http.base_url == "https://api.example.com"


def test_http_error_raises_super_send_tx_error() -> None:
    import urllib.error

    client = Ranla("rnl_test_key", base_url="https://api.example.com")
    payload = json.dumps({"error": {"message": "Invalid API key"}}).encode()
    http_error = urllib.error.HTTPError(
        url="https://api.example.com/emails",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=MagicMock(read=MagicMock(return_value=payload)),
    )

    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(SuperSendTXError) as exc:
            client.emails.send(
                from_="a@example.com",
                to="b@example.com",
                subject="Hi",
                html="<p>Hi</p>",
            )

    assert exc.value.status == 401
    assert exc.value.message == "Invalid API key"
