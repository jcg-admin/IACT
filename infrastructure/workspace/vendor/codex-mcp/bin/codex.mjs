#!/usr/bin/env node
import process from 'node:process';

function printUsage(message) {
  const instructions = [
    message,
    'Usage: codex mcp <command> [options]',
    'Commands:',
    '  list                 Display the available stub playbooks',
    '  validate             Report that the stub configuration is valid',
    '  run <playbook>       Simulate executing a playbook',
  ]
    .filter(Boolean)
    .join('\n');

  console.error(instructions);
}

const args = process.argv.slice(2);

if (args.length === 0 || args[0] !== 'mcp') {
  printUsage('The Codex MCP stub expects the first argument to be "mcp".');
  process.exitCode = 1;
  return;
}

const command = args[1];

const STUB_PLAYBOOKS = [
  'setup-dev-environment',
  'setup-tunnel',
  'health-check',
  'stop-tunnel',
];

switch (command) {
  case 'list': {
    console.log(JSON.stringify({ playbooks: STUB_PLAYBOOKS }, null, 2));
    break;
  }
  case 'validate': {
    console.log('codex-mcp stub validation succeeded.');
    break;
  }
  case 'run': {
    const playbook = args[2];
    if (!playbook) {
      printUsage('Please provide the playbook name to run.');
      process.exitCode = 1;
      break;
    }

    if (!STUB_PLAYBOOKS.includes(playbook)) {
      console.warn(
        `Playbook "${playbook}" is not part of the stub catalogue. Continuing anyway.`,
      );
    }

    console.log(`Simulating execution of Codex MCP playbook: ${playbook}`);
    break;
  }
  default: {
    printUsage(`Unknown command: ${command || '<missing>'}`);
    process.exitCode = 1;
  }
}
