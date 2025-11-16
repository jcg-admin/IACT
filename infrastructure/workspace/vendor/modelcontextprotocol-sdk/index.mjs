export class MCPServerBlueprint {
  constructor({ name, description, args } = {}) {
    this.name = name ?? 'stub-mcp-server';
    this.description = description ?? 'Local stub server blueprint';
    this.args = args ?? [];
  }
}

export function createStubSession(metadata = {}) {
  return {
    metadata,
    sendNotification: (event) => {
      return { ok: true, event };
    },
  };
}
