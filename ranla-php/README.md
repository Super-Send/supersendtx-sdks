# ranla

Official PHP client for the Ranla email API.

```bash
composer require ranla/ranla
```

```php
use Ranla\Client;

$client = new Client(getenv('RANLA_API_KEY'));

$email = $client->emails->send([
    'from' => 'ops@yourdomain.com',
    'to' => 'user@example.com',
    'subject' => 'Your receipt',
    'html' => '<p>Thanks for your purchase.</p>',
]);

echo $email['id'], ' ', $email['status'];
```

Defaults to `https://api.ranla.ai`. API keys may start with `rnl_` or `stx_`.

The legacy `supersendtx/supersendtx` package on Packagist remains supported.

## License

MIT
