# frozen_string_literal: true

require "base64"

module SuperSendTX
  # Maps a Mail::Message into emails.send keyword args.
  module MessageMapper
    HEADER_IDEMPOTENCY = "X-SuperSendTX-Idempotency-Key"
    HEADER_SCHEDULED_AT = "X-SuperSendTX-Scheduled-At"
    HEADER_TAG = "X-SuperSendTX-Tag"

    RESERVED_HEADERS = %w[
      from to cc bcc reply-to subject content-type mime-version date message-id
      x-supersendtx-idempotency-key x-supersendtx-scheduled-at x-supersendtx-tag
      idempotency-key
    ].freeze

    module_function

    def to_send_params(mail)
      from = format_addresses(mail[:from])
      raise ArgumentError, "Email is missing a From address." if from.empty?

      to = format_addresses(mail[:to])
      raise ArgumentError, "Email is missing a To recipient." if to.empty?

      html = html_body(mail)
      text = text_body(mail)
      raise ArgumentError, "Email must include html or text content." if html.nil? && text.nil?

      params = {
        from: from.length == 1 ? from[0] : from,
        to: to.length == 1 ? to[0] : to
      }
      params[:subject] = mail.subject if mail.subject && !mail.subject.empty?
      params[:html] = html if html
      params[:text] = text if text

      reply_to = format_addresses(mail[:reply_to])
      params[:reply_to] = reply_to.length == 1 ? reply_to[0] : reply_to unless reply_to.empty?

      cc = format_addresses(mail[:cc])
      params[:cc] = cc unless cc.empty?
      bcc = format_addresses(mail[:bcc])
      params[:bcc] = bcc unless bcc.empty?

      attachments = map_attachments(mail)
      params[:attachments] = attachments unless attachments.empty?

      tags = extract_tags(mail)
      params[:tags] = tags unless tags.empty?

      headers = extract_forward_headers(mail)
      params[:headers] = headers unless headers.empty?

      idem = header_value(mail, HEADER_IDEMPOTENCY) || header_value(mail, "Idempotency-Key")
      params[:idempotency_key] = idem if idem

      scheduled = header_value(mail, HEADER_SCHEDULED_AT)
      params[:scheduled_at] = scheduled if scheduled

      params
    end

    def format_addresses(field)
      return [] if field.nil?

      Array(field.addrs).filter_map do |addr|
        email = addr.address.to_s.strip
        next if email.empty?

        name = addr.display_name.to_s.strip
        name.empty? ? email : "#{name} <#{email}>"
      end
    end

    def html_body(mail)
      if mail.html_part
        mail.html_part.decoded
      elsif mail.mime_type == "text/html"
        mail.decoded
      end
    end

    def text_body(mail)
      if mail.text_part
        mail.text_part.decoded
      elsif mail.mime_type == "text/plain" || (!mail.multipart? && mail.mime_type.nil?)
        body = mail.body.decoded
        body && !body.empty? ? body : nil
      end
    end

    def map_attachments(mail)
      mail.attachments.map do |attachment|
        {
          "filename" => attachment.filename.to_s.empty? ? "attachment" : attachment.filename,
          "content_type" => attachment.mime_type || "application/octet-stream",
          "content" => Base64.strict_encode64(attachment.body.decoded)
        }
      end
    end

    def extract_tags(mail)
      values = mail.header[HEADER_TAG]
      return [] unless values

      list = values.respond_to?(:map) ? values.map(&:to_s) : [values.to_s]
      list.filter_map do |raw|
        trimmed = raw.strip
        next if trimmed.empty?

        if trimmed.include?("=")
          name, value = trimmed.split("=", 2)
          next if name.strip.empty? || value.strip.empty?

          { "name" => name.strip, "value" => value.strip }
        else
          { "name" => "tag", "value" => trimmed }
        end
      end
    end

    def extract_forward_headers(mail)
      out = {}
      mail.header.fields.each do |field|
        name = field.name.to_s
        lower = name.downcase
        next if RESERVED_HEADERS.include?(lower)
        next if lower.start_with?("content-")

        value = field.value.to_s.strip
        out[name] = value unless value.empty?
      end
      out
    end

    def header_value(mail, name)
      field = mail.header[name]
      return nil unless field

      value = field.respond_to?(:last) ? field.last.to_s : field.to_s
      value = value.strip
      value.empty? ? nil : value
    end
  end
end
