# frozen_string_literal: true

require "minitest/autorun"
require "mail"
require "supersendtx"

class DeliveryMethodTest < Minitest::Test
  def test_maps_and_sends_mail_message
    last_request = nil
    client = SuperSendTX::Client.new(
      "stx_test_key",
      base_url: "https://api.example.com",
      transport: lambda do |method, path, body, headers|
        last_request = { method: method, path: path, body: body, headers: headers }
        { "id" => "msg_rails_1", "status" => "queued" }
      end
    )

    mail = Mail.new do
      from "Ops <ops@example.com>"
      to "user@example.com"
      cc "cc@example.com"
      subject "Hello"
      html_part do
        content_type "text/html; charset=UTF-8"
        body "<p>Hi</p>"
      end
      text_part do
        body "Hi"
      end
    end
    mail.header["X-SuperSendTX-Tag"] = "campaign=welcome"
    mail.header["X-SuperSendTX-Idempotency-Key"] = "idem-rails"
    mail.header["X-Custom-Header"] = "keep"

    delivery = SuperSendTX::DeliveryMethod.new(client: client)
    result = delivery.deliver!(mail)

    assert_equal "msg_rails_1", result["id"]
    assert_equal "msg_rails_1", mail.message_id
    assert_equal "POST", last_request[:method]
    assert_equal "Ops <ops@example.com>", last_request[:body]["from"]
    assert_equal "user@example.com", last_request[:body]["to"]
    assert_equal [{ "name" => "campaign", "value" => "welcome" }], last_request[:body]["tags"]
    assert_equal "idem-rails", last_request[:headers]["Idempotency-Key"]
    assert_equal({ "X-Custom-Header" => "keep" }, last_request[:body]["headers"])
  end

  def test_message_mapper_requires_recipients
    mail = Mail.new do
      from "ops@example.com"
      subject "Hi"
      body "Hi"
    end

    error = assert_raises(ArgumentError) { SuperSendTX::MessageMapper.to_send_params(mail) }
    assert_match(/To recipient/, error.message)
  end

  def test_deliver_reraises_api_error_with_attributes
    client = SuperSendTX::Client.new(
      "stx_test_key",
      base_url: "https://api.example.com",
      transport: lambda do |_method, _path, _body, _headers|
        raise SuperSendTX::Error.new(
          "Invalid API key",
          status: 401,
          details: { "reason" => "bad_key" },
          error_code: "unauthorized"
        )
      end
    )

    mail = Mail.new do
      from "ops@example.com"
      to "user@example.com"
      body "Hi"
    end

    error = assert_raises(SuperSendTX::Error) do
      SuperSendTX::DeliveryMethod.new(client: client).deliver!(mail)
    end

    assert_match(/SuperSend TX API error: Invalid API key/, error.message)
    assert_equal 401, error.status
    assert_equal({ "reason" => "bad_key" }, error.details)
    assert_equal "unauthorized", error.error_code
  end
end
