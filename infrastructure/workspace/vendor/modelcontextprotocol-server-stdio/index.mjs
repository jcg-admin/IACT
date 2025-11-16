export function createMessageTransport() {
  return {
    input: process.stdin,
    output: process.stdout,
  };
}
