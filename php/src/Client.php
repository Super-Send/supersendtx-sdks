<?php

declare(strict_types=1);

namespace SuperSendTX;

final class Client
{
    private readonly HttpClient $http;

    public readonly EmailsResource $emails;
    public readonly DomainsResource $domains;
    public readonly WebhooksResource $webhooks;
    public readonly TemplatesResource $templates;
    public readonly SuppressionsResource $suppressions;

    /** @param callable(string, string, ?array<string, mixed>, array<string, string>): array<string, mixed>|null $transport */
    public function __construct(
        string $apiKey,
        string $baseUrl = HttpClient::DEFAULT_API_BASE_URL,
        mixed $transport = null,
    ) {
        $this->http = new HttpClient($apiKey, $baseUrl, $transport);
        $this->emails = new EmailsResource($this->http);
        $this->domains = new DomainsResource($this->http);
        $this->webhooks = new WebhooksResource($this->http);
        $this->templates = new TemplatesResource($this->http);
        $this->suppressions = new SuppressionsResource($this->http);
    }

    /**
     * @param array<string, mixed>|null $body
     * @param array<string, string> $headers
     *
     * @return array<string, mixed>
     */
    public function request(string $method, string $path, ?array $body = null, array $headers = []): array
    {
        return $this->http->request($method, $path, $body, $headers);
    }
}
