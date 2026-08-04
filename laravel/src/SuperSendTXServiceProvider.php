<?php

declare(strict_types=1);

namespace SuperSendTX\Laravel;

use Illuminate\Support\Facades\Mail;
use Illuminate\Support\ServiceProvider;
use SuperSendTX\Client;
use SuperSendTX\Symfony\Transport\SuperSendTXTransport;

class SuperSendTXServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->mergeConfigFrom(__DIR__.'/../config/supersendtx.php', 'supersendtx');

        $this->app->singleton(SuperSendTXManager::class, function ($app) {
            return new SuperSendTXManager($app['config']['supersendtx']);
        });

        $this->app->alias(SuperSendTXManager::class, 'supersendtx');

        $this->app->bind(Client::class, function ($app) {
            return $app->make(SuperSendTXManager::class)->client();
        });
    }

    public function boot(): void
    {
        if ($this->app->runningInConsole()) {
            $this->publishes([
                __DIR__.'/../config/supersendtx.php' => config_path('supersendtx.php'),
            ], 'supersendtx-config');
        }

        if (!$this->app->bound('mail.manager')) {
            return;
        }

        Mail::extend('supersendtx', function () {
            return new SuperSendTXTransport(
                $this->app->make(SuperSendTXManager::class)->client(),
            );
        });
    }
}
