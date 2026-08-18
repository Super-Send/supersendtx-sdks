# frozen_string_literal: true

require "minitest/autorun"
require "supersendtx"

class ClientTest < Minitest::Test
  def test_requires_stx_prefix
    error = assert_raises(ArgumentError) { SuperSendTX::Client.new("bad") }
    assert_match(/stx_ or rnl_/, error.message)
  end

  def test_accepts_rnl_prefix
    client = SuperSendTX::Client.new(
      "rnl_test_key",
      base_url: "https://api.example.com",
      transport: lambda { |_method, _path, _body, _headers| { "ok" => true } }
    )
    assert_instance_of SuperSendTX::Client, client
  end

  def test_emails_send
    last_request = nil

    client = SuperSendTX::Client.new(
      "stx_test_key",
      base_url: "https://api.example.com",
      transport: lambda do |method, path, body, headers|
        last_request = { method: method, path: path, body: body, headers: headers }
        { "id" => "msg_1", "status" => "sent" }
      end
    )

    result = client.emails.send(
      from: "a@example.com",
      to: "b@example.com",
      subject: "Hi",
      html: "<p>Hi</p>"
    )

    assert_equal({ "id" => "msg_1", "status" => "sent" }, result)
    assert_equal "POST", last_request[:method]
    assert_equal "/emails", last_request[:path]
    assert_equal "Bearer stx_test_key", last_request[:headers]["Authorization"]
  end

  def test_http_error_raises_super_send_tx_error
    client = SuperSendTX::Client.new(
      "stx_test_key",
      base_url: "https://api.example.com",
      transport: lambda do |_method, _path, _body, _headers|
        raise SuperSendTX::Error.from_response(401, { "error" => { "message" => "Invalid API key" } })
      end
    )

    error = assert_raises(SuperSendTX::Error) do
      client.emails.send(
        from: "a@example.com",
        to: "b@example.com",
        subject: "Hi",
        html: "<p>Hi</p>"
      )
    end

    assert_equal 401, error.status
    assert_equal "Invalid API key", error.message
  end
end
