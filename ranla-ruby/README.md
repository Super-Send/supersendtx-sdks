# ranla

Official Ruby client for the Ranla email API.

```bash
gem install ranla
```

```ruby
require "ranla"

client = Ranla::Client.new(ENV.fetch("RANLA_API_KEY"))

email = client.emails.send(
  from: "ops@yourdomain.com",
  to: "user@example.com",
  subject: "Your receipt",
  html: "<p>Thanks for your purchase.</p>"
)

puts email["id"], email["status"]
```

Defaults to `https://api.ranla.ai`. API keys may start with `rnl_` or `stx_`.

`Ranla::SuperSendTX` is the same class under the previous name.

The legacy `supersendtx` gem on RubyGems remains supported.

## License

MIT
