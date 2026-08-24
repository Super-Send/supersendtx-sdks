from __future__ import annotations

import pytest

pytest.importorskip("django")


def _ensure_django() -> None:
    import django
    from django.apps import apps
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            EMAIL_BACKEND="ranla.django.EmailBackend",
            SECRET_KEY="test",
            USE_I18N=False,
        )
    if not apps.ready:
        django.setup()


def test_django_email_backend_wraps_tx_class() -> None:
    from ranla.django import EmailBackend
    from ranla.django.email import EmailBackend as EmailBackendFromModule
    from supersendtx.django import EmailBackend as TxEmailBackend

    assert EmailBackend is EmailBackendFromModule
    assert EmailBackend is not TxEmailBackend
    assert issubclass(EmailBackend, TxEmailBackend)


def test_django_email_backend_defaults_to_ranla_host(monkeypatch: pytest.MonkeyPatch) -> None:
    _ensure_django()
    monkeypatch.delenv("SUPERSENDTX_API_KEY", raising=False)
    monkeypatch.delenv("SUPERSENDTX_BASE_URL", raising=False)
    monkeypatch.setenv("RANLA_API_KEY", "rnl_test_key")

    from ranla.client import DEFAULT_API_BASE_URL
    from ranla.django import EmailBackend

    backend = EmailBackend()
    assert backend._client._http.base_url == DEFAULT_API_BASE_URL


def test_django_email_backend_falls_back_to_tx_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _ensure_django()
    monkeypatch.delenv("RANLA_API_KEY", raising=False)
    monkeypatch.setenv("SUPERSENDTX_API_KEY", "stx_test_key")

    from ranla.client import DEFAULT_API_BASE_URL
    from ranla.django import EmailBackend

    backend = EmailBackend()
    assert backend._client._http.base_url == DEFAULT_API_BASE_URL


def test_django_email_backend_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _ensure_django()
    monkeypatch.delenv("RANLA_API_KEY", raising=False)
    monkeypatch.delenv("SUPERSENDTX_API_KEY", raising=False)

    from ranla.django import EmailBackend

    with pytest.raises(ValueError, match="RANLA_API_KEY"):
        EmailBackend()
