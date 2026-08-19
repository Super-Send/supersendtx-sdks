# frozen_string_literal: true

require "minitest/autorun"
require "ranla"

class RanlaClientTest < Minitest::Test
  def test_default_host_is_ranla
    last_request = nil

    client = Ranla::Client.new(
      "rnl_test_key",
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
    assert_equal "Bearer rnl_test_key", last_request[:headers]["Authorization"]
  end

  def test_super_send_tx_alias
    assert_equal Ranla::Client, Ranla::SuperSendTX
  end

  def test_requires_key_prefix
    error = assert_raises(ArgumentError) { Ranla::Client.new("bad") }
    assert_match(/stx_ or rnl_/, error.message)
  end
end
