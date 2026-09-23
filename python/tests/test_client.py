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
    with pytest.raises(ValueError, match="stx_ or rnl_"):
        SuperSendTX("bad")


def test_accepts_rnl_prefix() -> None:
    SuperSendTX("rnl_test_key", base_url="https://api.example.com")


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


def _json_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode()
    response.__enter__.return_value = response
    return response


def test_emails_send_forwards_category_and_unsubscribe(client: SuperSendTX) -> None:
    with patch("urllib.request.urlopen", return_value=_json_response({"id": "msg_1"})) as urlopen:
        client.emails.send(
            from_="a@example.com",
            to="b@example.com",
            subject="Hi",
            html="<p>Hi</p>",
            category="newsletter",
            unsubscribe=False,
        )

    body = json.loads(urlopen.call_args.args[0].data)
    assert body["category"] == "newsletter"
    assert body["unsubscribe"] is False


def test_emails_batch_forwards_category(client: SuperSendTX) -> None:
    with patch("urllib.request.urlopen", return_value=_json_response({"data": []})) as urlopen:
        client.emails.batch(
            [
                {"from": "a@example.com", "to": "b@example.com", "subject": "News", "html": "<p>1</p>", "category": "newsletter"},
                {"from": "a@example.com", "to": "c@example.com", "subject": "Receipt", "text": "2"},
            ]
        )

    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.example.com/emails/batch"
    emails = json.loads(request.data)["emails"]
    assert emails[0]["category"] == "newsletter"
    assert "category" not in emails[1]


def test_domains_list_sends_lowercase_booleans(client: SuperSendTX) -> None:
    with patch("urllib.request.urlopen", return_value=_json_response({"domains": []})) as urlopen:
        client.domains.list(inbound_enabled=True, limit=10)
        client.domains.list(inbound_enabled=False)
        client.domains.list()

    urls = [call.args[0].full_url for call in urlopen.call_args_list]
    assert urls == [
        "https://api.example.com/domains?limit=10&inbound_enabled=true",
        "https://api.example.com/domains?inbound_enabled=false",
        "https://api.example.com/domains",
    ]


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
