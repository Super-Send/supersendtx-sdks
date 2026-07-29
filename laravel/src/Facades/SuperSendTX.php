<?php

declare(strict_types=1);

namespace SuperSendTX\Laravel\Facades;

use Illuminate\Support\Facades\Facade;
use SuperSendTX\Client;

/**
 * @method static Client client()
 *
 * @see \SuperSendTX\Laravel\SuperSendTXManager
 */
final class SuperSendTX extends Facade
{
    protected static function getFacadeAccessor(): string
    {
        return 'supersendtx';
    }
}
