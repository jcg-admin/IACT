const DOMAIN_ENV_PREFIX = 'UI_BACKEND_';
const ENV_SUFFIX = '_SOURCE';
const VALID_SOURCES = ['api', 'mock'];

const normalizeDomain = (domain) => domain.toUpperCase();

const normalizeValue = (value) => {
  if (typeof value !== 'string') {
    return 'mock';
  }

  const normalized = value.trim().toLowerCase();

  if (VALID_SOURCES.includes(normalized)) {
    return normalized;
  }

  if (['true', '1', 'on', 'backend'].includes(normalized)) {
    return 'api';
  }

  return 'mock';
};

const buildEnvKey = (domain) => `${DOMAIN_ENV_PREFIX}${normalizeDomain(domain)}${ENV_SUFFIX}`;

export const getBackendSourceForDomain = (domain) => {
  const key = buildEnvKey(domain);
  const envValue = process.env[key];
  return normalizeValue(envValue);
};

export const shouldUseMockForDomain = (domain) => getBackendSourceForDomain(domain) !== 'api';
