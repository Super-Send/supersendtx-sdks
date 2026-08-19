# frozen_string_literal: true

require "supersendtx"

module Ranla
  class Client < SuperSendTX::Client
    DEFAULT_API_BASE_URL = "https://api.ranla.ai"

    def initialize(api_key, base_url: DEFAULT_API_BASE_URL, transport: nil)
      super(api_key, base_url: base_url, transport: transport)
    end
  end

  SuperSendTX = Client
end
