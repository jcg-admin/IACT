import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import appConfigReducer from '@state/slices/appConfigSlice';
import homeReducer from '@modules/home/state/homeSlice';
import App from './App';
import { setConfig } from '@state/slices/appConfigSlice';
import { AppConfigService } from '@services/config/AppConfigService';
import { CallsService } from '@services/calls/CallsService';

jest.mock('@services/config/AppConfigService', () => ({
  AppConfigService: {
    getConfig: jest.fn(),
  },
}));

jest.mock('@services/calls/CallsService', () => ({
  CallsService: {
    getCalls: jest.fn(),
  },
}));

const createTestStore = () => {
  return configureStore({
    reducer: {
      appConfig: appConfigReducer,
      home: homeReducer,
    },
  });
};

describe('App', () => {
  beforeEach(() => {
    AppConfigService.getConfig.mockResolvedValue({
      data: { featureFlags: { showMockBanner: true } },
      source: 'mock',
      error: new Error('No fue posible obtener la configuracion de la aplicacion: 500 Server Error'),
    });
    CallsService.getCalls.mockResolvedValue({
      data: { llamadas: [], estados: [], tipos: [] },
      source: 'api',
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    const store = createTestStore();
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  });

  it('renders main layout after loading', async () => {
    const store = createTestStore();
    store.dispatch(
      setConfig({
        config: { featureFlags: { showMockBanner: false } },
        source: 'api',
        errorMessage: null,
      })
    );

    render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    expect(await screen.findByRole('main')).toBeInTheDocument();
  });

  it('shows mock data banner when using mocks', async () => {
    const store = createTestStore();
    store.dispatch(
      setConfig({
        config: { featureFlags: { showMockBanner: true } },
        source: 'mock',
        errorMessage: 'Fallo API',
      })
    );

    render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    const banner = await screen.findByRole('status');
    expect(banner).toHaveTextContent(/Datos simulados/);
  });
});
