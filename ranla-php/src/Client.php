<?php

declare(strict_types=1);

namespace Ranla;

use SuperSendTX\Client as TxClient;

final class Client
{
    private readonly TxClient $inner;

    public readonly \SuperSendTX\EmailsResource $emails;
    public readonly \SuperSendTX\DomainsResource $domains;
    public readonly \SuperSendTX\WebhooksResource $webhooks;
    public readonly \SuperSendTX\TemplatesResource $templates;
    public readonly \SuperSendTX\SuppressionsResource $suppressions;

    public const DEFAULT_API_BASE_URL = 'https://api.ranla.ai';

    /** @param callable(string, string, ?array<string, mixed>, array<string, string>): array<string, mixed>|null $transport */
    public function __construct(
        string $apiKey,
        string $baseUrl = self::DEFAULT_API_BASE_URL,
        mixed $transport = null,
    ) {
        $this->inner = new TxClient($apiKey, $baseUrl, $transport);
        $this->emails = $this->inner->emails;
        $this->domains = $this->inner->domains;
        $this->webhooks = $this->inner->webhooks;
        $this->templates = $this->inner->templates;
        $this->suppressions = $this->inner->suppressions;
    }

    /**
     * @param array<string, mixed>|null $body
     * @param array<string, string> $headers
     *
     * @return array<string, mixed>
     */
    public function request(string $method, string $path, ?array $body = null, array $headers = []): array
    {
        return $this->inner->request($method, $path, $body, $headers);
    }
}
