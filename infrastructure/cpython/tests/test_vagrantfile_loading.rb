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
    attr_reader :network_calls, :providers, :synced_folders

    def initialize
      @post_up_message = nil
      @network_calls = []
      @providers = {}
      @synced_folders = []
    end

    def network(name, **options)
      @network_calls << [name, options]
    end

    def synced_folder(host_path, guest_path, **options)
      @synced_folders << {
        host: host_path,
        guest: guest_path,
        options: options
      }
    end

    def provider(name)
      provider = VirtualBoxProvider.new
      @providers[name.to_sym] = provider
      yield(provider)
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
    attr_reader :customizations

    def initialize
      @customizations = []
    end

    def customize(*args)
      @customizations << args.first
    end
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

  def test_virtualbox_customizations_avoid_removed_flags_and_duplicates
    vagrantfile = File.expand_path('../Vagrantfile', __dir__)

    load vagrantfile

    virtualbox = Vagrant.last_configuration.vm.providers[:virtualbox]
    refute_nil virtualbox, 'expected a virtualbox provider configuration'

    flags = virtualbox.customizations.map do |args|
      args.map { |arg| arg.is_a?(String) ? arg : arg.to_s }
    end

    refute flags.flatten.include?('--usbehci'), 'VirtualBox 7 removed EHCI support; do not call --usbehci'

    paravirt_calls = flags.count { |args| args.include?('--paravirtprovider') }
    assert_equal 1, paravirt_calls, 'paravirtprovider should be set exactly once'

    cpuexec_calls = flags.count { |args| args.include?('--cpuexecutioncap') }
    assert_equal 1, cpuexec_calls, 'cpuexecutioncap should be set exactly once'
  end

  def test_workspace_synced_folder_preserves_artifact_pipeline
    vagrantfile = File.expand_path('../Vagrantfile', __dir__)

    load vagrantfile

    synced_folders = Vagrant.last_configuration.vm.synced_folders
    refute_empty synced_folders, 'expected synced folders to be configured'

    workspace_mount = synced_folders.find { |entry| entry[:guest] == '/vagrant' }
    refute_nil workspace_mount, 'expected workspace directory to be mounted at /vagrant'

    assert_equal '.', workspace_mount[:host]

    options = workspace_mount[:options]
    assert_equal true, options[:create], 'workspace mount must create host directory for artifacts'
    assert_equal 'vagrant', options[:owner], 'workspace mount must be owned by vagrant user'
    assert_equal 'vagrant', options[:group], 'workspace mount must be owned by vagrant group'

    mount_options = options[:mount_options]
    refute_nil mount_options, 'workspace mount must specify mount options for permissions'
    assert_includes mount_options, 'dmode=755,fmode=664'
    assert_includes mount_options, 'iocharset=utf8'
    assert_includes mount_options, 'ttl=1'
  end

  def test_devcontainer_feature_consumes_local_artifact
    config_path = File.expand_path('../config/versions.conf', __dir__)
    config_contents = File.read(config_path)

    default_version = config_contents[/DEFAULT_PYTHON_VERSION="([^\"]+)"/, 1]
    default_build = config_contents[/DEFAULT_BUILD_NUMBER="([^\"]+)"/, 1]
    distro = config_contents[/DISTRO="([^\"]+)"/, 1]

    refute_nil default_version, 'expected DEFAULT_PYTHON_VERSION to be declared'
    refute_nil default_build, 'expected DEFAULT_BUILD_NUMBER to be declared'
    refute_nil distro, 'expected DISTRO to be declared'

    devcontainer_path = File.expand_path('../../../.devcontainer/devcontainer.json', __dir__)
    devcontainer_contents = File.read(devcontainer_path)

    expected_local_fragment = "infrastructure/cpython/artifacts/cpython-#{default_version}-#{distro}-build#{default_build}.tgz"
    assert_includes devcontainer_contents, expected_local_fragment,
      'Devcontainer must consume the artifact produced by the Vagrant builder'

    expected_release_fragment = "https://github.com/2-Coatl/IACT---project/releases/download/cpython-#{default_version}-build#{default_build}/cpython-#{default_version}-#{distro}-build#{default_build}.tgz"
    assert_includes devcontainer_contents, expected_release_fragment,
      'Devcontainer release template must reference the builder artifact naming'

    expected_local_checksum = "infrastructure/cpython/artifacts/cpython-#{default_version}-#{distro}-build#{default_build}.tgz.sha256"
    assert_includes devcontainer_contents, expected_local_checksum,
      'Devcontainer must pin the checksum generated by the Vagrant builder'

    expected_release_checksum = "https://github.com/2-Coatl/IACT---project/releases/download/cpython-#{default_version}-build#{default_build}/cpython-#{default_version}-#{distro}-build#{default_build}.tgz.sha256"
    assert_includes devcontainer_contents, expected_release_checksum,
      'Devcontainer release template must reference the checksum published by the builder'
  end
end
