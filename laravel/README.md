# SuperSend TX Laravel package

Laravel Mail transport and integration for the [SuperSend TX](https://supersendtx.com) transactional email API.

```bash
composer require supersendtx/laravel
```

Set in `.env`:

```bash
SUPERSENDTX_API_KEY=stx_your_key_here
MAIL_MAILER=supersendtx
```

Add to `config/mail.php`:

```php
'supersendtx' => [
    'transport' => 'supersendtx',
],
```

Then send as usual:

```php
Mail::to($user)->send(new WelcomeMail($user));
```

Optional: use the Facade / PHP client for direct API calls:

```php
use SuperSendTX\Laravel\Facades\SuperSendTX;

SuperSendTX::client()->emails->send([
    'from' => 'you@yourdomain.com',
    'to' => 'user@example.com',
    'subject' => 'Hello',
    'html' => '<p>It works.</p>',
]);
```

Docs: https://docs.supersendtx.com/frameworks/laravel
