# frozen_string_literal: true

require "json"
require "net/http"
require "uri"

module SuperSendTX
  class Error < StandardError
    attr_reader :status, :details, :error_code, :upgrade_url

    def initialize(message, status:, details: nil, error_code: nil, upgrade_url: nil)
      super(message)
      @status = status
      @details = details
      @error_code = error_code
      @upgrade_url = upgrade_url
    end

    def self.from_response(status, body)
      err = body.is_a?(Hash) ? body["error"] : nil

      case err
      when String
        new(err, status: status)
      when Hash
        new(
          err["message"] || "Request failed with status #{status}",
          status: status,
          details: err["details"],
          error_code: err["code"]&.to_s,
          upgrade_url: err["upgrade_url"]&.to_s
        )
      else
        new("Request failed with status #{status}", status: status)
      end
    end
  end
end
