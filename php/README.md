# SuperSend TX PHP SDK

Official PHP client for the [SuperSend TX](https://supersendtx.com) transactional email API.

```bash
composer require supersendtx/supersendtx
```

```php
<?php

use SuperSendTX\Client;

$tx = new Client('stx_your_key_here');

$result = $tx->emails->send([
    'from' => 'you@yourdomain.com',
    'to' => 'user@example.com',
    'subject' => 'Hello',
    'html' => '<p>It works.</p>',
]);

echo $result['id'], ' ', $result['status'], PHP_EOL;
```

Docs: https://docs.supersendtx.com/sdks/php
