# frozen_string_literal: true

module SuperSendTX
  class Client
    attr_reader :emails, :domains, :webhooks, :templates, :suppressions

    def initialize(api_key, base_url: HttpClient::DEFAULT_API_BASE_URL, transport: nil)
      http = HttpClient.new(api_key, base_url: base_url, transport: transport)
      @emails = EmailsResource.new(http)
      @domains = DomainsResource.new(http)
      @webhooks = WebhooksResource.new(http)
      @templates = TemplatesResource.new(http)
      @suppressions = SuppressionsResource.new(http)
      @http = http
    end

    def request(method, path, body: nil, headers: {})
      @http.request(method, path, body: body, headers: headers)
    end
  end
end
