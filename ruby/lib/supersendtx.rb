# frozen_string_literal: true

require_relative "supersendtx/version"
require_relative "supersendtx/error"
require_relative "supersendtx/http"
require_relative "supersendtx/resources"
require_relative "supersendtx/client"

module SuperSendTX
end

begin
  require "base64"
  require "mail"
rescue LoadError
  # base64/mail are optional; required for ActionMailer delivery method.
else
  require_relative "supersendtx/message_mapper"
  require_relative "supersendtx/delivery_method"
end

begin
  require "rails"
rescue LoadError
  # Rails is optional.
else
  require_relative "supersendtx/railtie"
end
