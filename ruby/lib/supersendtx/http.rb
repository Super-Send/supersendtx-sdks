# frozen_string_literal: true

require "json"
require "net/http"
require "uri"

module SuperSendTX
  class HttpClient
    DEFAULT_API_BASE_URL = "https://api.supersendtx.com"

    def initialize(api_key, base_url: DEFAULT_API_BASE_URL, transport: nil)
      raise ArgumentError, "SuperSend TX API key must start with stx_ or rnl_" unless api_key.start_with?("stx_", "rnl_")

      @api_key = api_key
      @base_url = base_url.chomp("/")
      @transport = transport
    end

    def request(method, path, body: nil, headers: {})
      request_headers = {
        "Authorization" => "Bearer #{@api_key}",
        "Content-Type" => "application/json"
      }.merge(headers)

      return @transport.call(method, path, body, request_headers) if @transport

      uri = URI.parse("#{@base_url}#{path}")
      http = Net::HTTP.new(uri.host, uri.port)
      http.use_ssl = uri.scheme == "https"

      request_class = Net::HTTP.const_get(method.capitalize)
      request = request_class.new(uri.request_uri)
      request_headers.each { |key, value| request[key] = value }
      request.body = JSON.generate(body) if body

      response = http.request(request)
      parsed = response.body.to_s.empty? ? {} : JSON.parse(response.body)

      raise Error.from_response(response.code.to_i, parsed) if response.code.to_i >= 400

      parsed
    end

    def query(params)
      filtered = params.compact
      return "" if filtered.empty?

      "?#{URI.encode_www_form(filtered)}"
    end
  end
end
