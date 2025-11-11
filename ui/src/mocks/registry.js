import configMock from './config.json';
import permissionsMock from './permissions.json';
import callsMock from './llamadas.json';
import { MOCK_METADATA } from './metadata';
import { validateConfigMock, validatePermissionsMock, validateCallsMock } from './schemas';

const DATA_BY_KEY = {
  config: configMock,
  permissions: permissionsMock,
  calls: callsMock,
};

const VALIDATORS = {
  config: validateConfigMock,
  permissions: validatePermissionsMock,
  calls: validateCallsMock,
};

export const validateMock = (key, data) => {
  const validator = VALIDATORS[key];
  if (!validator) {
    throw new Error(`Mock ${key} no esta registrado`);
  }

  return validator(data);
};

export const loadMock = (key) => {
  const data = DATA_BY_KEY[key];
  const metadata = MOCK_METADATA[key];

  if (!data || !metadata) {
    throw new Error(`Mock ${key} no esta registrado`);
  }

  const validated = validateMock(key, data);

  return { data: validated, metadata };
};

export const listRegisteredMocks = () => Object.keys(DATA_BY_KEY);
