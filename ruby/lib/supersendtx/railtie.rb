# frozen_string_literal: true

require "rails/railtie"
require_relative "delivery_method"

module SuperSendTX
  class Railtie < ::Rails::Railtie
    initializer "supersendtx.add_delivery_method" do
      ActiveSupport.on_load(:action_mailer) do
        ActionMailer::Base.add_delivery_method :supersendtx, SuperSendTX::DeliveryMethod
      end
    end
  end
end
