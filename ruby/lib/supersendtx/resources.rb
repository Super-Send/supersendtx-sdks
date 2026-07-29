# frozen_string_literal: true

module SuperSendTX
  class EmailsResource
    def initialize(http)
      @http = http
    end

    def list(limit: nil, cursor: nil)
      @http.request("GET", "/emails#{@http.query({ "limit" => limit, "cursor" => cursor })}")
    end

    def get(email_id)
      @http.request("GET", "/emails/#{URI.encode_www_form_component(email_id)}")
    end

    def send(from: nil, to: nil, **params)
      params["from"] = from if from
      params["to"] = to if to
      body = serialize_send_params(params)
      headers = {}
      idempotency_key = params["idempotency_key"] || params["idempotencyKey"]
      headers["Idempotency-Key"] = idempotency_key.to_s if idempotency_key

      @http.request("POST", "/emails", body: body, headers: headers)
    end

    def batch(emails)
      serialized = emails.map { |email| serialize_send_params(email) }
      @http.request("POST", "/emails/batch", body: { "emails" => serialized })
    end

    def cancel(email_id)
      @http.request("PATCH", "/emails/#{URI.encode_www_form_component(email_id)}", body: { "cancel" => true })
    end

    def resend(email_id)
      @http.request("POST", "/emails/#{URI.encode_www_form_component(email_id)}/resend")
    end

    def test_webhook(**params)
      @http.request("POST", "/emails/test", body: params)
    end

    def insights(window: "30d")
      @http.request("GET", "/deliverability#{@http.query({ "window" => window })}")
    end

    private

    def serialize_send_params(params)
      body = {
        "from" => params["from"] || params[:from],
        "to" => params["to"] || params[:to]
      }

      %w[subject html text reply_to replyTo cc bcc tags headers tag template].each do |key|
        value = params[key] || params[key.to_sym]
        next if value.nil?

        mapped = key == "replyTo" ? "reply_to" : key
        body[mapped] = value
      end

      body["html"] = params["htmlBody"] || params[:htmlBody] if params["htmlBody"] || params[:htmlBody]
      body["text"] = params["textBody"] || params[:textBody] if params["textBody"] || params[:textBody]
      body["scheduled_at"] = params["scheduled_at"] || params[:scheduled_at] if params["scheduled_at"] || params[:scheduled_at]
      body["scheduled_at"] ||= params["scheduledAt"] || params[:scheduledAt]
      body["unsubscribe"] = params["unsubscribe"] || params[:unsubscribe] if params.key?("unsubscribe") || params.key?(:unsubscribe)

      body
    end
  end

  class DomainsResource
    def initialize(http)
      @http = http
    end

    def list(limit: nil, cursor: nil, inbound_enabled: nil)
      @http.request(
        "GET",
        "/domains#{@http.query({ "limit" => limit, "cursor" => cursor, "inbound_enabled" => inbound_enabled })}"
      )
    end

    def get(id_or_name)
      @http.request("GET", "/domains/#{URI.encode_www_form_component(id_or_name)}")
    end

    def create(name, inbound_enabled: nil)
      body = { "name" => name }
      body["inbound_enabled"] = inbound_enabled unless inbound_enabled.nil?
      @http.request("POST", "/domains", body: body)
    end

    def verify(id_or_name)
      @http.request("POST", "/domains/#{URI.encode_www_form_component(id_or_name)}", body: { "action" => "verify" })
    end

    def apply(id_or_name, provider: "cloudflare", credentials: nil)
      body = { "action" => "apply", "provider" => provider }
      body["credentials"] = credentials if credentials
      @http.request("POST", "/domains/#{URI.encode_www_form_component(id_or_name)}", body: body)
    end

    def update(id_or_name, **params)
      @http.request("PATCH", "/domains/#{URI.encode_www_form_component(id_or_name)}", body: params)
    end

    def delete(id_or_name)
      @http.request("DELETE", "/domains/#{URI.encode_www_form_component(id_or_name)}")
    end
  end

  class WebhooksResource
    def initialize(http)
      @http = http
    end

    def list(limit: nil, cursor: nil)
      @http.request("GET", "/webhooks#{@http.query({ "limit" => limit, "cursor" => cursor })}")
    end

    def get(webhook_id)
      @http.request("GET", "/webhooks/#{URI.encode_www_form_component(webhook_id)}")
    end

    def create(**params)
      @http.request("POST", "/webhooks", body: params)
    end

    def update(webhook_id, **params)
      @http.request("PATCH", "/webhooks/#{URI.encode_www_form_component(webhook_id)}", body: params)
    end

    def delete(webhook_id)
      @http.request("DELETE", "/webhooks/#{URI.encode_www_form_component(webhook_id)}")
    end
  end

  class TemplatesResource
    def initialize(http)
      @http = http
    end

    def list(limit: nil, cursor: nil, status: nil)
      @http.request(
        "GET",
        "/templates#{@http.query({ "limit" => limit, "cursor" => cursor, "status" => status })}"
      )
    end

    def get(id_or_alias)
      @http.request("GET", "/templates/#{URI.encode_www_form_component(id_or_alias)}")
    end

    def create(**params)
      @http.request("POST", "/templates", body: params)
    end

    def update(id_or_alias, **params)
      @http.request("PATCH", "/templates/#{URI.encode_www_form_component(id_or_alias)}", body: params)
    end

    def delete(id_or_alias)
      @http.request("DELETE", "/templates/#{URI.encode_www_form_component(id_or_alias)}")
    end

    def publish(id_or_alias)
      @http.request("POST", "/templates/#{URI.encode_www_form_component(id_or_alias)}", body: { "action" => "publish" })
    end
  end

  class SuppressionsResource
    def initialize(http)
      @http = http
    end

    def list(limit: nil, cursor: nil, email: nil)
      @http.request(
        "GET",
        "/suppressions#{@http.query({ "limit" => limit, "cursor" => cursor, "email" => email })}"
      )
    end

    def create(**params)
      @http.request("POST", "/suppressions", body: params)
    end

    def remove(id_or_email)
      if id_or_email.include?("@")
        return @http.request("DELETE", "/suppressions#{@http.query({ "email" => id_or_email })}")
      end

      @http.request("DELETE", "/suppressions/#{URI.encode_www_form_component(id_or_email)}")
    end
  end
end
