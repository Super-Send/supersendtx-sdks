from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from supersendtx import SuperSendTX
from supersendtx.errors import SuperSendTXError


@pytest.fixture
def client() -> SuperSendTX:
    return SuperSendTX("stx_test_key", base_url="https://api.example.com")


def test_requires_stx_prefix() -> None:
    with pytest.raises(ValueError, match="stx_"):
        SuperSendTX("bad")


def test_emails_send(client: SuperSendTX) -> None:
    response = MagicMock()
    response.read.return_value = json.dumps({"id": "msg_1", "status": "sent"}).encode()
    response.__enter__.return_value = response

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        result = client.emails.send(
            from_="a@example.com",
            to="b@example.com",
            subject="Hi",
            html="<p>Hi</p>",
        )

    assert result == {"id": "msg_1", "status": "sent"}
    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.example.com/emails"
    assert request.method == "POST"
    assert request.get_header("Authorization") == "Bearer stx_test_key"


def test_http_error_raises_super_send_tx_error(client: SuperSendTX) -> None:
    import urllib.error

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
