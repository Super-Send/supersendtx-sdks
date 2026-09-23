<?php

declare(strict_types=1);

namespace SuperSendTX\Tests;

use PHPUnit\Framework\TestCase;
use SuperSendTX\Client;
use SuperSendTX\SuperSendTXError;

final class ClientTest extends TestCase
{
    public function testRequiresStxPrefix(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('stx_ or rnl_');

        new Client('bad');
    }

    public function testAcceptsRnlPrefix(): void
    {
        $client = new Client(
            'rnl_test_key',
            'https://api.example.com',
            static fn (): array => ['ok' => true],
        );

        self::assertInstanceOf(Client::class, $client);
    }

    public function testEmailsSend(): void
    {
        $lastRequest = null;

        $client = new Client(
            'stx_test_key',
            'https://api.example.com',
            function (string $method, string $path, ?array $body, array $headers) use (&$lastRequest): array {
                $lastRequest = compact('method', 'path', 'body', 'headers');

                return ['id' => 'msg_1', 'status' => 'sent'];
            },
        );

        $result = $client->emails->send([
            'from' => 'a@example.com',
            'to' => 'b@example.com',
            'subject' => 'Hi',
            'html' => '<p>Hi</p>',
        ]);

        self::assertSame(['id' => 'msg_1', 'status' => 'sent'], $result);
        self::assertSame('POST', $lastRequest['method']);
        self::assertSame('/emails', $lastRequest['path']);
        self::assertSame('Bearer stx_test_key', $lastRequest['headers']['Authorization'] ?? null);
    }

    public function testEmailsSendIncludesAttachmentsAndIdempotency(): void
    {
        $lastRequest = null;

        $client = new Client(
            'stx_test_key',
            'https://api.example.com',
            function (string $method, string $path, ?array $body, array $headers) use (&$lastRequest): array {
                $lastRequest = compact('method', 'path', 'body', 'headers');

                return ['id' => 'msg_2', 'status' => 'queued'];
            },
        );

        $client->emails->send([
            'from' => 'a@example.com',
            'to' => 'b@example.com',
            'subject' => 'Hi',
            'html' => '<p>Hi</p>',
            'attachments' => [
                [
                    'filename' => 'note.txt',
                    'content_type' => 'text/plain',
                    'content' => base64_encode('hello'),
                ],
            ],
            'idempotency_key' => 'idem-1',
        ]);

        self::assertSame('idem-1', $lastRequest['headers']['Idempotency-Key'] ?? null);
        self::assertSame(
            [
                [
                    'filename' => 'note.txt',
                    'content_type' => 'text/plain',
                    'content' => base64_encode('hello'),
                ],
            ],
            $lastRequest['body']['attachments'] ?? null,
        );
    }

    public function testEmailsSendForwardsCategoryAndUnsubscribe(): void
    {
        $lastRequest = null;

        $client = new Client(
            'stx_test_key',
            'https://api.example.com',
            function (string $method, string $path, ?array $body, array $headers) use (&$lastRequest): array {
                $lastRequest = compact('method', 'path', 'body', 'headers');

                return ['id' => 'msg_3', 'status' => 'queued'];
            },
        );

        $client->emails->send([
            'from' => 'a@example.com',
            'to' => 'b@example.com',
            'subject' => 'Hi',
            'html' => '<p>Hi</p>',
            'category' => 'newsletter',
            'unsubscribe' => false,
        ]);

        self::assertSame('newsletter', $lastRequest['body']['category'] ?? null);
        self::assertFalse($lastRequest['body']['unsubscribe'] ?? null);
    }

    public function testEmailsBatchForwardsCategory(): void
    {
        $lastRequest = null;

        $client = new Client(
            'stx_test_key',
            'https://api.example.com',
            function (string $method, string $path, ?array $body, array $headers) use (&$lastRequest): array {
                $lastRequest = compact('method', 'path', 'body', 'headers');

                return ['data' => []];
            },
        );

        $client->emails->batch([
            ['from' => 'a@example.com', 'to' => 'b@example.com', 'subject' => 'News', 'html' => '<p>1</p>', 'category' => 'product'],
            ['from' => 'a@example.com', 'to' => 'c@example.com', 'subject' => 'Receipt', 'text' => '2'],
        ]);

        self::assertSame('/emails/batch', $lastRequest['path']);
        self::assertSame('product', $lastRequest['body']['emails'][0]['category'] ?? null);
        self::assertArrayNotHasKey('category', $lastRequest['body']['emails'][1]);
    }

    public function testHttpErrorRaisesSuperSendTxError(): void
    {
        $client = new Client(
            'stx_test_key',
            'https://api.example.com',
            function (): array {
                throw SuperSendTXError::fromResponse(401, ['error' => ['message' => 'Invalid API key']]);
            },
        );

        $this->expectException(SuperSendTXError::class);
        $this->expectExceptionMessage('Invalid API key');

        $client->emails->send([
            'from' => 'a@example.com',
            'to' => 'b@example.com',
            'subject' => 'Hi',
            'html' => '<p>Hi</p>',
        ]);
    }
}
