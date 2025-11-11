import { renderHook, act } from '@testing-library/react';
import { useCallsSummary } from './useCallsSummary';
import callsMock from '@mocks/llamadas.json';
import { CallsService } from '@services/calls/CallsService';

jest.mock('@services/calls/CallsService', () => ({
  CallsService: {
    getCalls: jest.fn(),
  },
}));

describe('useCallsSummary', () => {
  beforeEach(() => {
    CallsService.getCalls.mockResolvedValue({
      data: callsMock,
      source: 'api',
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('aggregates metrics from calls payload', async () => {
    const { result } = renderHook(() => useCallsSummary());

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.summary.totalCalls).toBe(3);
    expect(result.current.summary.activeCalls).toBe(1);
    expect(result.current.summary.completedCalls).toBe(2);
    expect(result.current.source).toBe('api');
    expect(result.current.error).toBeNull();
  });

  it('propagates fallback metadata when mocks are used', async () => {
    CallsService.getCalls.mockResolvedValueOnce({
      data: callsMock,
      source: 'mock',
      error: new Error('Fallo backend'),
    });

    const { result } = renderHook(() => useCallsSummary());

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.source).toBe('mock');
    expect(result.current.error).toMatch(/Fallo backend/);
  });
});
