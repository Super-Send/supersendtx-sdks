<?php

declare(strict_types=1);

namespace SuperSendTX;

final class SuperSendTXError extends \RuntimeException
{
    public function __construct(
        string $message,
        public readonly int $status,
        public readonly mixed $details = null,
        public readonly ?string $errorCode = null,
        public readonly ?string $upgradeUrl = null,
    ) {
        parent::__construct($message, $status);
    }

    /**
     * @param array<string, mixed> $body
     */
    public static function fromResponse(int $status, array $body): self
    {
        $err = $body['error'] ?? null;

        if (is_string($err)) {
            return new self($err, $status);
        }

        if (is_array($err)) {
            $message = (string) ($err['message'] ?? "Request failed with status {$status}");
            $details = $err['details'] ?? null;
            $errorCode = isset($err['code']) ? (string) $err['code'] : null;
            $upgradeUrl = isset($err['upgrade_url']) ? (string) $err['upgrade_url'] : null;

            return new self($message, $status, $details, $errorCode, $upgradeUrl);
        }

        return new self("Request failed with status {$status}", $status);
    }
}
