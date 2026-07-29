<?php

declare(strict_types=1);

namespace SuperSendTX;

final class EmailsResource
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /**
     * @return array<string, mixed>
     */
    public function list(?int $limit = null, ?string $cursor = null): array
    {
        return $this->http->request('GET', '/emails'.$this->http->query([
            'limit' => $limit,
            'cursor' => $cursor,
        ]));
    }

    /**
     * @return array<string, mixed>
     */
    public function get(string $emailId): array
    {
        return $this->http->request('GET', '/emails/'.rawurlencode($emailId));
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function send(array $params): array
    {
        $body = self::serializeSendParams($params);
        $headers = [];
        $idempotencyKey = $params['idempotency_key'] ?? $params['idempotencyKey'] ?? null;
        if ($idempotencyKey !== null) {
            $headers['Idempotency-Key'] = (string) $idempotencyKey;
        }

        return $this->http->request('POST', '/emails', $body, $headers);
    }

    /**
     * @param list<array<string, mixed>> $emails
     *
     * @return array<string, mixed>
     */
    public function batch(array $emails): array
    {
        $serialized = array_map(self::serializeSendParams(...), $emails);

        return $this->http->request('POST', '/emails/batch', ['emails' => $serialized]);
    }

    /**
     * @return array<string, mixed>
     */
    public function cancel(string $emailId): array
    {
        return $this->http->request('PATCH', '/emails/'.rawurlencode($emailId), ['cancel' => true]);
    }

    /**
     * @return array<string, mixed>
     */
    public function resend(string $emailId): array
    {
        return $this->http->request('POST', '/emails/'.rawurlencode($emailId).'/resend');
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function testWebhook(array $params): array
    {
        return $this->http->request('POST', '/emails/test', $params);
    }

    /**
     * @return array<string, mixed>
     */
    public function insights(string $window = '30d'): array
    {
        return $this->http->request('GET', '/deliverability'.$this->http->query(['window' => $window]));
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    private static function serializeSendParams(array $params): array
    {
        $body = [
            'from' => $params['from'],
            'to' => $params['to'],
        ];

        foreach (['subject', 'html', 'text', 'reply_to', 'replyTo', 'cc', 'bcc', 'tags', 'headers', 'tag', 'template'] as $key) {
            if (!array_key_exists($key, $params) || $params[$key] === null) {
                continue;
            }
            $mapped = $key === 'replyTo' ? 'reply_to' : $key;
            $body[$mapped] = $params[$key];
        }

        if (array_key_exists('htmlBody', $params) && $params['htmlBody'] !== null) {
            $body['html'] = $params['htmlBody'];
        }
        if (array_key_exists('textBody', $params) && $params['textBody'] !== null) {
            $body['text'] = $params['textBody'];
        }
        if (array_key_exists('scheduled_at', $params) && $params['scheduled_at'] !== null) {
            $body['scheduled_at'] = $params['scheduled_at'];
        }
        if (array_key_exists('scheduledAt', $params) && $params['scheduledAt'] !== null) {
            $body['scheduled_at'] = $params['scheduledAt'];
        }
        if (array_key_exists('unsubscribe', $params) && $params['unsubscribe'] !== null) {
            $body['unsubscribe'] = $params['unsubscribe'];
        }

        return $body;
    }
}

final class DomainsResource
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /**
     * @return array<string, mixed>
     */
    public function list(?int $limit = null, ?string $cursor = null, ?bool $inboundEnabled = null): array
    {
        return $this->http->request('GET', '/domains'.$this->http->query([
            'limit' => $limit,
            'cursor' => $cursor,
            'inbound_enabled' => $inboundEnabled,
        ]));
    }

    /**
     * @return array<string, mixed>
     */
    public function get(string $idOrName): array
    {
        return $this->http->request('GET', '/domains/'.rawurlencode($idOrName));
    }

    /**
     * @return array<string, mixed>
     */
    public function create(string $name, ?bool $inboundEnabled = null): array
    {
        $body = ['name' => $name];
        if ($inboundEnabled !== null) {
            $body['inbound_enabled'] = $inboundEnabled;
        }

        return $this->http->request('POST', '/domains', $body);
    }

    /**
     * @return array<string, mixed>
     */
    public function verify(string $idOrName): array
    {
        return $this->http->request('POST', '/domains/'.rawurlencode($idOrName), ['action' => 'verify']);
    }

    /**
     * @param array<string, mixed>|null $credentials
     *
     * @return array<string, mixed>
     */
    public function apply(string $idOrName, string $provider = 'cloudflare', ?array $credentials = null): array
    {
        $body = ['action' => 'apply', 'provider' => $provider];
        if ($credentials !== null) {
            $body['credentials'] = $credentials;
        }

        return $this->http->request('POST', '/domains/'.rawurlencode($idOrName), $body);
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function update(string $idOrName, array $params): array
    {
        return $this->http->request('PATCH', '/domains/'.rawurlencode($idOrName), $params);
    }

    /**
     * @return array<string, mixed>
     */
    public function delete(string $idOrName): array
    {
        return $this->http->request('DELETE', '/domains/'.rawurlencode($idOrName));
    }
}

final class WebhooksResource
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /**
     * @return array<string, mixed>
     */
    public function list(?int $limit = null, ?string $cursor = null): array
    {
        return $this->http->request('GET', '/webhooks'.$this->http->query([
            'limit' => $limit,
            'cursor' => $cursor,
        ]));
    }

    /**
     * @return array<string, mixed>
     */
    public function get(string $webhookId): array
    {
        return $this->http->request('GET', '/webhooks/'.rawurlencode($webhookId));
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function create(array $params): array
    {
        return $this->http->request('POST', '/webhooks', $params);
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function update(string $webhookId, array $params): array
    {
        return $this->http->request('PATCH', '/webhooks/'.rawurlencode($webhookId), $params);
    }

    /**
     * @return array<string, mixed>
     */
    public function delete(string $webhookId): array
    {
        return $this->http->request('DELETE', '/webhooks/'.rawurlencode($webhookId));
    }
}

final class TemplatesResource
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /**
     * @return array<string, mixed>
     */
    public function list(?int $limit = null, ?string $cursor = null, ?string $status = null): array
    {
        return $this->http->request('GET', '/templates'.$this->http->query([
            'limit' => $limit,
            'cursor' => $cursor,
            'status' => $status,
        ]));
    }

    /**
     * @return array<string, mixed>
     */
    public function get(string $idOrAlias): array
    {
        return $this->http->request('GET', '/templates/'.rawurlencode($idOrAlias));
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function create(array $params): array
    {
        return $this->http->request('POST', '/templates', $params);
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function update(string $idOrAlias, array $params): array
    {
        return $this->http->request('PATCH', '/templates/'.rawurlencode($idOrAlias), $params);
    }

    /**
     * @return array<string, mixed>
     */
    public function delete(string $idOrAlias): array
    {
        return $this->http->request('DELETE', '/templates/'.rawurlencode($idOrAlias));
    }

    /**
     * @return array<string, mixed>
     */
    public function publish(string $idOrAlias): array
    {
        return $this->http->request('POST', '/templates/'.rawurlencode($idOrAlias), ['action' => 'publish']);
    }
}

final class SuppressionsResource
{
    public function __construct(private readonly HttpClient $http)
    {
    }

    /**
     * @return array<string, mixed>
     */
    public function list(?int $limit = null, ?string $cursor = null, ?string $email = null): array
    {
        return $this->http->request('GET', '/suppressions'.$this->http->query([
            'limit' => $limit,
            'cursor' => $cursor,
            'email' => $email,
        ]));
    }

    /**
     * @param array<string, mixed> $params
     *
     * @return array<string, mixed>
     */
    public function create(array $params): array
    {
        return $this->http->request('POST', '/suppressions', $params);
    }

    /**
     * @return array<string, mixed>
     */
    public function remove(string $idOrEmail): array
    {
        if (str_contains($idOrEmail, '@')) {
            return $this->http->request('DELETE', '/suppressions'.$this->http->query(['email' => $idOrEmail]));
        }

        return $this->http->request('DELETE', '/suppressions/'.rawurlencode($idOrEmail));
    }
}
