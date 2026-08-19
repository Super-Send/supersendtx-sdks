# frozen_string_literal: true

require_relative "lib/ranla/version"

Gem::Specification.new do |spec|
  spec.name = "ranla"
  spec.version = Ranla::VERSION
  spec.authors = ["Ranla"]
  spec.email = ["support@ranla.ai"]

  spec.summary = "Ranla email API client for Ruby"
  spec.description = "Official Ruby client for the Ranla REST API."
  spec.homepage = "https://ranla.ai"
  spec.license = "MIT"
  spec.required_ruby_version = ">= 3.1.0"

  spec.metadata = {
    "homepage_uri" => spec.homepage,
    "source_code_uri" => "https://github.com/Super-Send/supersendtx-sdks/tree/main/ranla-ruby",
    "documentation_uri" => "https://docs.ranla.ai/sdks/ruby",
    "rubygems_mfa_required" => "true"
  }

  spec.files = Dir.chdir(__dir__) do
    `git ls-files -z`.split("\x0").reject { |f| f.start_with?("spec/") }
  rescue StandardError
    Dir.glob("{lib}/**/*", base: __dir__) + ["README.md", "ranla.gemspec", "Gemfile"]
  end

  spec.require_paths = ["lib"]

  spec.add_dependency "supersendtx", "~> 0.8.5"
  spec.add_development_dependency "minitest", "~> 5.25"
end
