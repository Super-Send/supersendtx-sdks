# SuperSend TX Ruby SDK

Official Ruby client for the [SuperSend TX](https://supersendtx.com) transactional email API.

```bash
gem install supersendtx
```

```ruby
require "supersendtx"

tx = SuperSendTX::Client.new("stx_your_key_here")

result = tx.emails.send(
  from: "you@yourdomain.com",
  to: "user@example.com",
  subject: "Hello",
  html: "<p>It works.</p>"
)

puts result["id"], result["status"]
```

## Rails ActionMailer

```ruby
config.action_mailer.delivery_method = :supersendtx
config.action_mailer.supersendtx_settings = {
  api_key: ENV.fetch("SUPERSENDTX_API_KEY")
}
```

Docs: https://docs.supersendtx.com/sdks/ruby
