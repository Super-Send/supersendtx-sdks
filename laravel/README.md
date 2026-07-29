# SuperSend TX Laravel package

Laravel integration for the [SuperSend TX](https://supersendtx.com) transactional email API.

```bash
composer require supersendtx/laravel
```

Publish config:

```bash
php artisan vendor:publish --tag=supersendtx-config
```

Set `SUPERSENDTX_API_KEY` in `.env`, then send:

```php
use SuperSendTX\Laravel\Facades\SuperSendTX;

$result = SuperSendTX::client()->emails->send([
    'from' => 'you@yourdomain.com',
    'to' => 'user@example.com',
    'subject' => 'Hello',
    'html' => '<p>It works.</p>',
]);
```

Docs: https://docs.supersendtx.com/frameworks/laravel
