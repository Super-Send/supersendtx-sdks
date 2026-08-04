# frozen_string_literal: true

require_relative "lib/supersendtx/version"

Gem::Specification.new do |spec|
  spec.name = "supersendtx"
  spec.version = SuperSendTX::VERSION
  spec.authors = ["SuperSend TX"]
  spec.email = ["support@supersendtx.com"]

  spec.summary = "SuperSend TX transactional email API client for Ruby"
  spec.description = "Official Ruby client for the SuperSend TX REST API."
  spec.homepage = "https://supersendtx.com"
  spec.license = "MIT"
  spec.required_ruby_version = ">= 3.1.0"

  spec.metadata = {
    "homepage_uri" => spec.homepage,
    "source_code_uri" => "https://github.com/Super-Send/supersendtx-sdks/tree/main/ruby",
    "documentation_uri" => "https://docs.supersendtx.com/sdks/ruby",
    "rubygems_mfa_required" => "true"
  }

  spec.files = Dir.chdir(__dir__) do
    `git ls-files -z`.split("\x0").reject { |f| f.start_with?("spec/") }
  rescue StandardError
    Dir.glob("{lib}/**/*", base: __dir__) + ["README.md", "supersendtx.gemspec"]
  end

  spec.require_paths = ["lib"]

  spec.add_dependency "base64", ">= 0.2"
  spec.add_development_dependency "mail", ">= 2.8"
  spec.add_development_dependency "minitest", "~> 5.25"
end
