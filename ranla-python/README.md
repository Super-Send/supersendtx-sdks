# ranla

Official Python client for the Ranla email API.

```bash
pip install ranla
```

```python
import os
from ranla import Ranla

client = Ranla(os.environ["RANLA_API_KEY"])

email = client.emails.send(
    from_="ops@yourdomain.com",
    to="user@example.com",
    subject="Your receipt",
    html="<p>Thanks for your purchase.</p>",
)
print(email["id"], email["status"])
```

Defaults to `https://api.ranla.ai`. API keys may start with `rnl_` or `stx_`.

`SuperSendTX` is the same class under the previous name:

```python
from ranla import SuperSendTX
```

The legacy `supersendtx` package on PyPI remains supported.

## License

MIT
