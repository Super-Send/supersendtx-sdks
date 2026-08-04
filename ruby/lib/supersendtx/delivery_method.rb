# frozen_string_literal: true

require "mail"
require_relative "message_mapper"

module SuperSendTX
  # ActionMailer delivery method: config.action_mailer.delivery_method = :supersendtx
  class DeliveryMethod
    def initialize(settings = {})
      @settings = settings || {}
      @client = @settings[:client] || build_client
    end

    def deliver!(mail)
      params = MessageMapper.to_send_params(mail)
      result = @client.emails.send(**params)
      message_id = result.is_a?(Hash) ? (result["id"] || result[:id]) : nil
      mail.message_id = message_id if message_id && mail.respond_to?(:message_id=)
      result
    rescue SuperSendTX::Error => e
      # Re-raise as SuperSendTX::Error (not a bare String → RuntimeError) so
      # ActionMailer / rescue_from can read status, details, and error_code.
      raise SuperSendTX::Error.new(
        "SuperSend TX API error: #{e.message}",
        status: e.status,
        details: e.details,
        error_code: e.error_code,
        upgrade_url: e.upgrade_url
      )
    end

    private

    def build_client
      api_key = @settings[:api_key] || @settings["api_key"] || ENV["SUPERSENDTX_API_KEY"]
      raise ArgumentError, "SUPERSENDTX_API_KEY is not configured." if api_key.nil? || api_key.to_s.empty?

      base_url = @settings[:base_url] || @settings["base_url"] || ENV["SUPERSENDTX_BASE_URL"]
      if base_url && !base_url.to_s.empty?
        Client.new(api_key, base_url: base_url)
      else
        Client.new(api_key)
      end
    end
  end
end
