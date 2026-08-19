<?php

declare(strict_types=1);

namespace Ranla\Tests;

use PHPUnit\Framework\TestCase;
use Ranla\Client;

final class ClientTest extends TestCase
{
    public function test_default_host_is_ranla(): void
    {
        $lastUrl = null;
        $client = new Client(
            'rnl_test_key',
            transport: function (string $method, string $path, ?array $body, array $headers) use (&$lastUrl): array {
                $lastUrl = $path;
                return ['id' => 'msg_1', 'status' => 'sent'];
            },
        );

        $result = $client->emails->send([
            'from' => 'a@example.com',
            'to' => 'b@example.com',
            'subject' => 'Hi',
            'html' => '<p>Hi</p>',
        ]);

        $this->assertSame(['id' => 'msg_1', 'status' => 'sent'], $result);
        $this->assertSame('/emails', $lastUrl);
    }

    public function test_base_url_override(): void
    {
        $client = new Client(
            'rnl_test_key',
            'https://api.example.com',
            transport: static fn (): array => ['ok' => true],
        );

        $this->assertSame(['ok' => true], $client->request('GET', '/health'));
    }
}
