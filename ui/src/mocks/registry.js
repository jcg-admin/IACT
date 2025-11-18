import configMock from './config.json';
import permissionsMock from './permissions.json';
import callsMock from './llamadas.json';
import healthMock from './health.json';
import usuariosMock from './usuarios.json';
import dashboardMock from './dashboard.json';
import configuracionMock from './configuracion.json';
import configurationMock from './configuration.json';
import presupuestosMock from './presupuestos.json';
import politicasMock from './politicas.json';
import excepcionesMock from './excepciones.json';
import reportesMock from './reportes.json';
import notificationsMock from './notifications.json';
import etlMock from './etl.json';
import doraMock from './dora.json';
import { MOCK_METADATA } from './metadata';
import {
  validateConfigMock,
  validatePermissionsMock,
  validateCallsMock,
  validateHealthMock,
  validateUsersMock,
  validateDashboardMock,
  validateConfiguracionMock,
  validateConfigurationMock,
  validatePresupuestosMock,
  validatePoliticasMock,
  validateExcepcionesMock,
  validateReportesMock,
  validateNotificationsMock,
  validateETLMock,
  validateDORAMock,
} from './schemas';

const DATA_BY_KEY = {
  config: configMock,
  permissions: permissionsMock,
  calls: callsMock,
  health: healthMock,
  users: usuariosMock,
  dashboard: dashboardMock,
  configuracion: configuracionMock,
  configuration: configurationMock,
  presupuestos: presupuestosMock,
  politicas: politicasMock,
  excepciones: excepcionesMock,
  reportes: reportesMock,
  notifications: notificationsMock,
  etl: etlMock,
  dora: doraMock,
};

const VALIDATORS = {
  config: validateConfigMock,
  permissions: validatePermissionsMock,
  calls: validateCallsMock,
  health: validateHealthMock,
  users: validateUsersMock,
  dashboard: validateDashboardMock,
  configuracion: validateConfiguracionMock,
  configuration: validateConfigurationMock,
  presupuestos: validatePresupuestosMock,
  politicas: validatePoliticasMock,
  excepciones: validateExcepcionesMock,
  reportes: validateReportesMock,
  notifications: validateNotificationsMock,
  etl: validateETLMock,
  dora: validateDORAMock,
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
