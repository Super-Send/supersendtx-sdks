<?php

declare(strict_types=1);

namespace SuperSendTX\Laravel;

use SuperSendTX\Client;
use SuperSendTX\HttpClient;

final class SuperSendTXManager
{
    private ?Client $client = null;

    /** @param array{api_key?: string|null, base_url?: string|null} $config */
    public function __construct(private readonly array $config)
    {
    }

    public function client(): Client
    {
        if ($this->client !== null) {
            return $this->client;
        }

        $apiKey = $this->config['api_key'] ?? null;
        if (!is_string($apiKey) || $apiKey === '') {
            throw new \InvalidArgumentException('SUPERSENDTX_API_KEY is not configured.');
        }

        $baseUrl = $this->config['base_url'] ?? HttpClient::DEFAULT_API_BASE_URL;
        if (!is_string($baseUrl) || $baseUrl === '') {
            $baseUrl = HttpClient::DEFAULT_API_BASE_URL;
        }

        return $this->client = new Client($apiKey, $baseUrl);
    }
}
