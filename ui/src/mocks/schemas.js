const isObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);

const assert = (condition, message) => {
  if (!condition) {
    throw new Error(message);
  }
};

const validateConfigMock = (data) => {
  assert(isObject(data), 'config debe ser un objeto');
  assert(isObject(data.featureFlags), 'config.featureFlags debe ser un objeto');
  assert(typeof data.featureFlags.useCallsMock === 'boolean', 'featureFlags.useCallsMock debe ser booleano');
  assert(typeof data.featureFlags.showMockBanner === 'boolean', 'featureFlags.showMockBanner debe ser booleano');
  assert(isObject(data.branding), 'config.branding debe ser un objeto');
  assert(typeof data.branding.productName === 'string', 'branding.productName debe ser string');
  assert(typeof data.branding.supportEmail === 'string', 'branding.supportEmail debe ser string');
  assert(isObject(data.endpoints), 'config.endpoints debe ser un objeto');
  ['calls', 'permissions', 'announcements'].forEach((key) => {
    assert(typeof data.endpoints[key] === 'string', `endpoints.${key} debe ser string`);
  });
  return data;
};

const validateGroup = (group) => {
  assert(isObject(group), 'grupo invalido');
  assert(typeof group.id === 'number', 'grupo.id debe ser numero');
  assert(typeof group.codigo === 'string', 'grupo.codigo debe ser string');
  assert(typeof group.nombre_display === 'string', 'grupo.nombre_display debe ser string');
};

const validateFunction = (entry) => {
  assert(isObject(entry), 'funcion invalida');
  assert(typeof entry.id === 'number', 'funcion.id debe ser numero');
  ['nombre', 'nombre_completo', 'dominio', 'icono'].forEach((key) => {
    assert(typeof entry[key] === 'string', `funcion.${key} debe ser string`);
  });
  assert(typeof entry.orden_menu === 'number', 'funcion.orden_menu debe ser numero');
};

const validatePermissionsMock = (data) => {
  assert(isObject(data), 'permissions debe ser un objeto');
  assert(isObject(data.user), 'permissions.user debe ser objeto');
  assert(typeof data.user.id === 'number', 'user.id debe ser numero');
  assert(typeof data.user.username === 'string', 'user.username debe ser string');
  assert(typeof data.user.email === 'string', 'user.email debe ser string');
  assert(Array.isArray(data.user.grupos), 'user.grupos debe ser arreglo');
  data.user.grupos.forEach(validateGroup);
  assert(Array.isArray(data.capacidades), 'capacidades debe ser arreglo');
  data.capacidades.forEach((cap) => assert(typeof cap === 'string', 'capacidad debe ser string'));
  assert(Array.isArray(data.funciones_accesibles), 'funciones_accesibles debe ser arreglo');
  data.funciones_accesibles.forEach(validateFunction);
  return data;
};

const validateCallType = (type) => {
  assert(isObject(type), 'tipo invalido');
  assert(typeof type.id === 'number', 'tipo.id debe ser numero');
  assert(typeof type.codigo === 'string', 'tipo.codigo debe ser string');
  assert(typeof type.nombre === 'string', 'tipo.nombre debe ser string');
};

const validateCallState = (state) => {
  assert(isObject(state), 'estado invalido');
  assert(typeof state.id === 'number', 'estado.id debe ser numero');
  assert(typeof state.codigo === 'string', 'estado.codigo debe ser string');
  assert(typeof state.nombre === 'string', 'estado.nombre debe ser string');
  assert(typeof state.es_final === 'boolean', 'estado.es_final debe ser booleano');
};

const validateCall = (call) => {
  assert(isObject(call), 'llamada invalida');
  assert(typeof call.id === 'number', 'llamada.id debe ser numero');
  assert(typeof call.codigo === 'string', 'llamada.codigo debe ser string');
  assert(typeof call.numero_telefono === 'string', 'llamada.numero_telefono debe ser string');
  validateCallType(call.tipo);
  validateCallState(call.estado);
  assert(isObject(call.agente), 'llamada.agente debe ser objeto');
  assert(typeof call.agente.id === 'number', 'agente.id debe ser numero');
  assert(typeof call.agente.username === 'string', 'agente.username debe ser string');
  assert(typeof call.cliente_nombre === 'string', 'cliente_nombre debe ser string');
  assert(typeof call.cliente_email === 'string', 'cliente_email debe ser string');
  assert(typeof call.fecha_inicio === 'string', 'fecha_inicio debe ser string');
  assert(call.fecha_fin === null || typeof call.fecha_fin === 'string', 'fecha_fin debe ser string o null');
  assert(call.duracion === null || typeof call.duracion === 'number', 'duracion debe ser numero o null');
  assert(isObject(call.metadata), 'llamada.metadata debe ser objeto');
  ['motivo', 'producto', 'prioridad'].forEach((key) => {
    assert(typeof call.metadata[key] === 'string', `metadata.${key} debe ser string`);
  });
  assert(typeof call.notas === 'string', 'llamada.notas debe ser string');
};

const validateCallsMock = (data) => {
  assert(isObject(data), 'calls debe ser objeto');
  assert(Array.isArray(data.llamadas), 'calls.llamadas debe ser arreglo');
  data.llamadas.forEach(validateCall);
  assert(Array.isArray(data.estados), 'calls.estados debe ser arreglo');
  data.estados.forEach((state) => {
    validateCallState(state);
    assert(typeof state.activo === 'boolean', 'estado.activo debe ser booleano');
  });
  assert(Array.isArray(data.tipos), 'calls.tipos debe ser arreglo');
  data.tipos.forEach((type) => {
    validateCallType(type);
    assert(typeof type.activo === 'boolean', 'tipo.activo debe ser booleano');
  });
  return data;
};

const validateHealthMock = (data) => {
  assert(isObject(data), 'health debe ser objeto');
  assert(typeof data.status === 'string', 'health.status debe ser string');
  assert(typeof data.checkedAt === 'string', 'health.checkedAt debe ser string');

  if (data.services) {
    assert(Array.isArray(data.services), 'health.services debe ser arreglo cuando existe');
    data.services.forEach((svc) => {
      assert(isObject(svc), 'health.services[x] debe ser objeto');
      assert(typeof svc.name === 'string', 'health.services[x].name debe ser string');
      assert(typeof svc.status === 'string', 'health.services[x].status debe ser string');
    });
  }

  return data;
};

module.exports = {
  validateConfigMock,
  validatePermissionsMock,
  validateCallsMock,
  validateHealthMock,
};
