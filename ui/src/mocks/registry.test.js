import { loadMock, validateMock } from './registry';

describe('mocks registry', () => {
  it('returns validated data with metadata', () => {
    const { data, metadata } = loadMock('config');

    expect(data).toHaveProperty('featureFlags');
    expect(metadata).toMatchObject({ id: 'config', source: expect.any(String), lastUpdated: expect.any(String) });
  });

  it('throws when validation fails', () => {
    expect(() => validateMock('config', { featureFlags: null })).toThrow('config');
  });

  it('throws for unknown mock keys', () => {
    expect(() => loadMock('unknown')).toThrow('unknown');
  });
});
