import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import appConfigReducer from '@state/slices/appConfigSlice';
import homeReducer from '@modules/home/state/homeSlice';
import App from './App';

const createTestStore = () => {
  return configureStore({
    reducer: {
      appConfig: appConfigReducer,
      home: homeReducer,
    },
  });
};

describe('App', () => {
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
    store.dispatch({ type: 'appConfig/setLoading', payload: false });

    render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
