from __future__ import annotations

from typing import Any

from supersendtx.http import HttpClient


class EmailsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, *, limit: int | None = None, cursor: str | None = None) -> dict[str, Any]:
        return self._http.request("GET", f"/emails{self._http.query({'limit': limit, 'cursor': cursor})}")

    def get(self, email_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/emails/{email_id}")

    def send(
        self,
        *,
        from_: str | None = None,
        to: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to
        body = _serialize_send_params(params)
        headers: dict[str, str] = {}
        idempotency_key = params.get("idempotency_key") or params.get("idempotencyKey")
        if idempotency_key:
            headers["Idempotency-Key"] = str(idempotency_key)
        return self._http.request("POST", "/emails", body=body, headers=headers)

    def batch(self, emails: list[dict[str, Any]]) -> dict[str, Any]:
        serialized = [_serialize_send_params(email) for email in emails]
        return self._http.request("POST", "/emails/batch", body={"emails": serialized})

    def cancel(self, email_id: str) -> dict[str, Any]:
        return self._http.request("PATCH", f"/emails/{email_id}", body={"cancel": True})

    def resend(self, email_id: str) -> dict[str, Any]:
        return self._http.request("POST", f"/emails/{email_id}/resend")

    def test_webhook(self, **params: Any) -> dict[str, Any]:
        return self._http.request("POST", "/emails/test", body=params)

    def insights(self, *, window: str = "30d") -> dict[str, Any]:
        return self._http.request("GET", f"/deliverability{self._http.query({'window': window})}")


class DomainsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        inbound_enabled: bool | None = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            f"/domains{self._http.query({'limit': limit, 'cursor': cursor, 'inbound_enabled': inbound_enabled})}",
        )

    def get(self, id_or_name: str) -> dict[str, Any]:
        return self._http.request("GET", f"/domains/{id_or_name}")

    def create(self, name: str, *, inbound_enabled: bool | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if inbound_enabled is not None:
            body["inbound_enabled"] = inbound_enabled
        return self._http.request("POST", "/domains", body=body)

    def verify(self, id_or_name: str) -> dict[str, Any]:
        return self._http.request("POST", f"/domains/{id_or_name}", body={"action": "verify"})

    def apply(
        self,
        id_or_name: str,
        *,
        provider: str = "cloudflare",
        credentials: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"action": "apply", "provider": provider}
        if credentials:
            body["credentials"] = credentials
        return self._http.request("POST", f"/domains/{id_or_name}", body=body)

    def update(self, id_or_name: str, **params: Any) -> dict[str, Any]:
        return self._http.request("PATCH", f"/domains/{id_or_name}", body=params)

    def delete(self, id_or_name: str) -> dict[str, Any]:
        return self._http.request("DELETE", f"/domains/{id_or_name}")


class WebhooksResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, *, limit: int | None = None, cursor: str | None = None) -> dict[str, Any]:
        return self._http.request(
            "GET",
            f"/webhooks{self._http.query({'limit': limit, 'cursor': cursor})}",
        )

    def get(self, webhook_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/webhooks/{webhook_id}")

    def create(self, **params: Any) -> dict[str, Any]:
        return self._http.request("POST", "/webhooks", body=params)

    def update(self, webhook_id: str, **params: Any) -> dict[str, Any]:
        return self._http.request("PATCH", f"/webhooks/{webhook_id}", body=params)

    def delete(self, webhook_id: str) -> dict[str, Any]:
        return self._http.request("DELETE", f"/webhooks/{webhook_id}")


class TemplatesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            f"/templates{self._http.query({'limit': limit, 'cursor': cursor, 'status': status})}",
        )

    def get(self, id_or_alias: str) -> dict[str, Any]:
        return self._http.request("GET", f"/templates/{id_or_alias}")

    def create(self, **params: Any) -> dict[str, Any]:
        return self._http.request("POST", "/templates", body=params)

    def update(self, id_or_alias: str, **params: Any) -> dict[str, Any]:
        return self._http.request("PATCH", f"/templates/{id_or_alias}", body=params)

    def delete(self, id_or_alias: str) -> dict[str, Any]:
        return self._http.request("DELETE", f"/templates/{id_or_alias}")

    def publish(self, id_or_alias: str) -> dict[str, Any]:
        return self._http.request("POST", f"/templates/{id_or_alias}", body={"action": "publish"})


class SuppressionsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            f"/suppressions{self._http.query({'limit': limit, 'cursor': cursor, 'email': email})}",
        )

    def create(self, **params: Any) -> dict[str, Any]:
        return self._http.request("POST", "/suppressions", body=params)

    def remove(self, id_or_email: str) -> dict[str, Any]:
        if "@" in id_or_email:
            return self._http.request("DELETE", f"/suppressions{self._http.query({'email': id_or_email})}")
        return self._http.request("DELETE", f"/suppressions/{id_or_email}")


def _serialize_send_params(params: dict[str, Any]) -> dict[str, Any]:
    body: dict[str, Any] = {
        "from": params["from"],
        "to": params["to"],
    }
    for key in (
        "subject",
        "html",
        "text",
        "reply_to",
        "replyTo",
        "cc",
        "bcc",
        "tags",
        "headers",
        "tag",
        "template",
        "attachments",
    ):
        if key in params and params[key] is not None:
            mapped = "reply_to" if key == "replyTo" else key
            body[mapped] = params[key]
    if params.get("htmlBody") is not None:
        body["html"] = params["htmlBody"]
    if params.get("textBody") is not None:
        body["text"] = params["textBody"]
    if params.get("scheduled_at") is not None:
        body["scheduled_at"] = params["scheduled_at"]
    if params.get("scheduledAt") is not None:
        body["scheduled_at"] = params["scheduledAt"]
    if params.get("unsubscribe") is not None:
        body["unsubscribe"] = params["unsubscribe"]
    return body
