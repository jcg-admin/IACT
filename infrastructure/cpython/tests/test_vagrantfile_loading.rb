require 'minitest/autorun'
require 'tmpdir'

# Minimal Vagrant DSL stubs to allow loading the Vagrantfile in tests
module Vagrant
  class << self
    attr_reader :last_configuration

    def configure(_version)
      @last_configuration = Configuration.new
      yield(@last_configuration)
    end

    def has_plugin?(_name)
      false
    end
  end

  class Configuration
    attr_reader :vm, :ssh

    def initialize
      @vm = VMConfig.new
      @ssh = SSHConfig.new
    end
  end

  class VMConfig
    attr_accessor :box, :box_check_update, :box_version, :hostname
    attr_reader :network_calls

    def initialize
      @post_up_message = nil
      @network_calls = []
    end

    def network(name, **options)
      @network_calls << [name, options]
    end

    def synced_folder(*_args); end

    def provider(_name)
      yield(VirtualBoxProvider.new)
    end

    def provision(*_args); end

    def post_up_message=(value)
      @post_up_message = value
    end
  end

  class SSHConfig
    attr_accessor :forward_agent, :insert_key, :connect_timeout
  end

  class VirtualBoxProvider
    attr_accessor :name, :memory, :cpus, :gui, :linked_clone

    def customize(*_args); end
  end
end

class VagrantfileLoadingTest < Minitest::Test
  def setup
    @original_home = ENV['HOME']
    @tmp_home = Dir.mktmpdir
    ENV['HOME'] = @tmp_home
  end

  def teardown
    ENV['HOME'] = @original_home
    require 'fileutils'
    FileUtils.remove_entry(@tmp_home)
  end

  def test_private_network_uses_named_internal_network
    vagrantfile = File.expand_path('../Vagrantfile', __dir__)

    load vagrantfile

    network_calls = Vagrant.last_configuration.vm.network_calls
    private_network = network_calls.find { |name, _| name == "private_network" }
    refute_nil private_network, 'expected a private_network configuration to be present'
    options = private_network[1]
    assert_kind_of String, options[:virtualbox__intnet], 'virtualbox__intnet must specify an internal network name'
  end
end
