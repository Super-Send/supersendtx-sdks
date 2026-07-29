<?php

declare(strict_types=1);

namespace SuperSendTX\Laravel\Tests;

use PHPUnit\Framework\TestCase;
use SuperSendTX\Laravel\SuperSendTXManager;

final class SuperSendTXManagerTest extends TestCase
{
    public function testRequiresApiKey(): void
    {
        $manager = new SuperSendTXManager(['api_key' => null]);

        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('SUPERSENDTX_API_KEY is not configured.');

        $manager->client();
    }

    public function testBuildsAndCachesClient(): void
    {
        $manager = new SuperSendTXManager([
            'api_key' => 'stx_test_key',
            'base_url' => 'https://api.example.com',
        ]);

        $client = $manager->client();

        self::assertSame($client, $manager->client());
    }
}
