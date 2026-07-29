# SuperSend TX Python SDK

Official Python client for the [SuperSend TX](https://supersendtx.com) transactional email API.

```bash
pip install supersendtx
```

```python
from supersendtx import SuperSendTX

tx = SuperSendTX("stx_your_key_here")

result = tx.emails.send(
    from_="you@yourdomain.com",
    to="user@example.com",
    subject="Hello",
    html="<p>It works.</p>",
)

print(result["id"], result["status"])
```

Docs: https://docs.supersendtx.com/sdks/python
