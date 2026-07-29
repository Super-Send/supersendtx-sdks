<?php

declare(strict_types=1);

namespace SuperSendTX;

final class HttpClient
{
    public const DEFAULT_API_BASE_URL = 'https://api.supersendtx.com';

    /** @param callable(string, string, ?array<string, mixed>, array<string, string>): array<string, mixed>|null $transport */
    public function __construct(
        private readonly string $apiKey,
        private readonly string $baseUrl = self::DEFAULT_API_BASE_URL,
        private readonly mixed $transport = null,
    ) {
        if (!str_starts_with($apiKey, 'stx_')) {
            throw new \InvalidArgumentException('SuperSend TX API key must start with stx_');
        }
    }

    /**
     * @param array<string, mixed>|null $body
     * @param array<string, string> $headers
     *
     * @return array<string, mixed>
     */
    public function request(string $method, string $path, ?array $body = null, array $headers = []): array
    {
        $requestHeaders = array_merge([
            'Authorization' => 'Bearer '.$this->apiKey,
            'Content-Type' => 'application/json',
        ], $headers);

        if ($this->transport !== null) {
            return ($this->transport)($method, $path, $body, $requestHeaders);
        }

        $url = rtrim($this->baseUrl, '/').$path;
        $payload = $body !== null ? json_encode($body, JSON_THROW_ON_ERROR) : null;

        $formattedHeaders = $this->formatHeaders($requestHeaders);

        $context = stream_context_create([
            'http' => [
                'method' => $method,
                'header' => implode("\r\n", $formattedHeaders),
                'content' => $payload ?? '',
                'ignore_errors' => true,
            ],
        ]);

        $raw = file_get_contents($url, false, $context);
        if ($raw === false) {
            throw new \RuntimeException('Request failed');
        }

        $status = $this->responseStatus($http_response_header ?? []);
        $parsed = $raw !== '' ? json_decode($raw, true) : [];

        if (!is_array($parsed)) {
            $parsed = [];
        }

        if ($status >= 400) {
            throw SuperSendTXError::fromResponse($status, $parsed);
        }

        return $parsed;
    }

    /**
     * @param array<string, mixed> $params
     */
    public function query(array $params): string
    {
        $filtered = array_filter($params, static fn ($value) => $value !== null);
        if ($filtered === []) {
            return '';
        }

        return '?'.http_build_query($filtered);
    }

    /**
     * @param array<string, string> $headers
     *
     * @return list<string>
     */
    private function formatHeaders(array $headers): array
    {
        $formatted = [];
        foreach ($headers as $key => $value) {
            $formatted[] = "{$key}: {$value}";
        }

        return $formatted;
    }

    /**
     * @param list<string> $headers
     */
    private function responseStatus(array $headers): int
    {
        foreach ($headers as $header) {
            if (preg_match('/^HTTP\/\d\.\d\s+(\d+)/', $header, $matches) === 1) {
                return (int) $matches[1];
            }
        }

        return 200;
    }
}
