---
id: UI-README
titulo: IACT UI - Modular Monolith Frontend
version: 0.1.0
fecha_creacion: 2025-11-06
---

# IACT UI - Modular Monolith Frontend

Frontend de React para el sistema IACT (IVR Analytics & Customer Tracking).

---

## Arquitectura

**Patrón**: Modular Monolith (ver ADR_011)

El frontend está organizado como un **monolito modular**, no microfrontends. Cada módulo es autónomo pero todos comparten:
- Redux store único
- Webpack build único
- Dependencias compartidas (React, Redux Toolkit)

### Ventajas de Modular Monolith

1. **Simplicidad**: Un solo build, un solo deploy
2. **Performance**: No overhead de comunicación entre microfrontends
3. **Desarrollo rápido**: Refactorings globales son simples
4. **Testing integrado**: Tests end-to-end naturales
5. **Code sharing**: Componentes/hooks compartidos sin complejidad

---

## Estructura de Directorios

```
ui/
├── public/
│   └── index.html              HTML base
├── src/
│   ├── app/
│   │   ├── App.jsx            Componente raíz
│   │   └── App.test.jsx       Tests de App
│   ├── components/            Componentes compartidos
│   │   └── MainLayout.jsx
│   ├── hooks/                 Hooks compartidos
│   │   └── useAppConfig.js
│   ├── modules/               Módulos de negocio (autónomos)
│   │   └── home/
│   │       ├── hooks/         Hooks del módulo
│   │       ├── state/         Redux slice del módulo
│   │       ├── HomeModule.jsx Componente principal
│   │       └── index.js       Export público
│   ├── pages/                 Páginas (componen módulos)
│   │   └── HomePage.jsx
│   ├── state/                 Redux global
│   │   ├── slices/
│   │   └── store.js
│   ├── styles/                Estilos globales
│   │   └── global.css
│   └── index.jsx              Entry point
├── webpack/                   Configuración Webpack
├── babel.config.cjs           Configuración Babel
├── jest.setup.js              Setup de Jest
├── package.json               Dependencias
├── webpack.config.cjs         Webpack config
└── README.md                  Este archivo
```

---

## Principios de Módulos

### Anatomía de un Módulo

```
modules/example/
├── hooks/                  Hooks del módulo (useExampleData)
├── state/                  Redux slice del módulo
│   ├── exampleSlice.js
│   └── exampleSlice.test.js
├── components/             Componentes internos (opcional)
├── ExampleModule.jsx       Componente principal
└── index.js                Export: export { default } from './ExampleModule'
```

### Reglas de Módulos

1. **Autónomo**: Cada módulo maneja su propio estado (slice de Redux)
2. **Encapsulado**: Exports mínimos (solo componente principal vía index.js)
3. **Sin dependencias entre módulos**: Módulos NO importan otros módulos directamente
4. **Comunicación via Redux**: Si necesitan compartir datos, usar Redux store
5. **Hooks locales**: Los hooks del módulo solo los usa el módulo

---

## Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React** | 18.3.1 | UI library |
| **Redux Toolkit** | 2.2.5 | State management (ver ADR_012) |
| **Webpack** | 5.95.0 | Module bundler (ver ADR_013) |
| **Babel** | 7.25.2 | Transpilación |
| **Jest** | 29.7.0 | Testing framework |
| **Testing Library** | 16.0.0 | React testing utilities |

### ¿Por qué Redux Toolkit y no Context API?

Ver **ADR_012** para justificación completa. Resumen:
- Dashboard con 10 widgets requiere estado complejo
- Performance crítica (<3s carga)
- DevTools para debugging
- Middleware para side effects (futuro)

### ¿Por qué Webpack y no Vite?

Ver **ADR_013**. Resumen:
- Ecosistema maduro y estable
- Configuración explícita y predecible
- Alias paths configurados (@app, @modules, @components)
- Code splitting para producción

---

## Comandos Disponibles

### Desarrollo

```bash
# Instalar dependencias
npm install

# Iniciar dev server (http://localhost:3000)
npm start

# Build para producción
npm run build

# Ejecutar tests
npm test

# Tests en watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Dev Server

- **Puerto**: 3000
- **Hot Module Replacement**: Activo
- **Proxy API**: Configurar en webpack.config.cjs si necesario

---

## Path Aliases

Configurados en `webpack.config.cjs` y `jest.config` (package.json):

```javascript
import App from '@app/App';                    // src/app/
import HomeModule from '@modules/home';        // src/modules/
import MainLayout from '@components/MainLayout'; // src/components/
import { useAppConfig } from '@hooks/useAppConfig'; // src/hooks/
import '@styles/global.css';                   // src/styles/
import { store } from '@state/store';          // src/state/
```

**Beneficios**:
- Imports limpios sin `../../../../`
- Refactoring más fácil
- Autocomplete en IDEs

---

## Testing

### Estrategia

1. **Unit tests**: Redux slices (homeSlice.test.js)
2. **Component tests**: React components (App.test.jsx)
3. **Integration tests**: Flujos completos (futuro)

### Configuración

- **Environment**: jsdom (simula browser)
- **Setup**: jest.setup.js (mocks globales)
- **Coverage mínimo**: 80% (objetivo)

### Convenciones

```javascript
// Nombrar tests con .test.jsx o .test.js
describe('ComponentName', () => {
  it('does something', () => {
    // Arrange
    // Act
    // Assert
  });
});
```

---

## Estado Global (Redux)

### Store Structure

```javascript
{
  appConfig: {      // Configuración global de la app
    config: {},
    isLoading: false,
    error: null
  },
  home: {           // Estado del módulo home
    announcement: '',
    isLoading: false,
    error: null
  },
  // Futuros módulos agregarán sus propios slices
}
```

### Crear Nuevo Slice

```javascript
// src/modules/example/state/exampleSlice.js
import { createSlice } from '@reduxjs/toolkit';

const exampleSlice = createSlice({
  name: 'example',
  initialState: { /* ... */ },
  reducers: {
    // actions
  },
});

export const { /* actions */ } = exampleSlice.actions;
export default exampleSlice.reducer;
```

Luego agregar al store en `src/state/store.js`:

```javascript
import exampleReducer from '@modules/example/state/exampleSlice';

export const store = configureStore({
  reducer: {
    appConfig: appConfigReducer,
    home: homeReducer,
    example: exampleReducer,  // Agregar aquí
  },
});
```

---

## Crear Nuevo Módulo

### 1. Estructura

```bash
mkdir -p src/modules/mynewmodule/{hooks,state}
```

### 2. Slice de Redux

```javascript
// src/modules/mynewmodule/state/mynewmoduleSlice.js
import { createSlice } from '@reduxjs/toolkit';

const mynewmoduleSlice = createSlice({
  name: 'mynewmodule',
  initialState: { data: null, isLoading: false, error: null },
  reducers: {
    setData: (state, action) => { state.data = action.payload; },
    setLoading: (state, action) => { state.isLoading = action.payload; },
  },
});

export const { setData, setLoading } = mynewmoduleSlice.actions;
export default mynewmoduleSlice.reducer;
```

### 3. Hook personalizado (opcional)

```javascript
// src/modules/mynewmodule/hooks/useMyNewModule.js
import { useSelector, useDispatch } from 'react-redux';
import { setData } from '../state/mynewmoduleSlice';

export function useMyNewModule() {
  const dispatch = useDispatch();
  const { data } = useSelector((state) => state.mynewmodule);

  const loadData = () => {
    // lógica
    dispatch(setData(/* ... */));
  };

  return { data, loadData };
}
```

### 4. Componente principal

```javascript
// src/modules/mynewmodule/MyNewModule.jsx
import { useMyNewModule } from './hooks/useMyNewModule';

function MyNewModule() {
  const { data } = useMyNewModule();
  return <div>{/* render */}</div>;
}

export default MyNewModule;
```

### 5. Export público

```javascript
// src/modules/mynewmodule/index.js
export { default } from './MyNewModule';
```

### 6. Registrar en store

Agregar reducer en `src/state/store.js`.

### 7. Usar en página

```javascript
// src/pages/MyNewPage.jsx
import MyNewModule from '@modules/mynewmodule';

function MyNewPage() {
  return <MyNewModule />;
}
```

---

## Estilos

### Global Styles

- Ubicación: `src/styles/global.css`
- Importado en: `src/index.jsx`
- Reset CSS básico incluido

### Component Styles

**Opciones**:

1. **CSS Modules** (recomendado para módulos grandes):
```javascript
import styles from './MyComponent.module.css';
<div className={styles.container}>...</div>
```

2. **Inline styles** (para estilos dinámicos):
```javascript
<div style={{ color: isActive ? 'blue' : 'gray' }}>...</div>
```

3. **Global classes** (para layouts):
```javascript
<div className="main-layout">...</div>
```

---

## Performance

### Optimizaciones Actuales

1. **Code splitting**: Webpack splitChunks en producción
2. **Source maps**: Solo en desarrollo (source-map en prod)
3. **Cache busting**: [contenthash] en nombres de archivos
4. **Tree shaking**: Automático en producción

### Métricas Objetivo

| Métrica | Target |
|---------|--------|
| Dashboard carga | <3 segundos |
| Widget individual | <2 segundos |
| Bundle size (gzipped) | <500 KB |
| Time to Interactive | <5 segundos |

---

## Restricciones del Sistema IACT

El UI debe respetar las restricciones del backend:

1. **NO real-time updates**: Dashboard se actualiza con datos del ETL (6-12h)
2. **Usuario refresca manualmente**: F5 para actualizar datos
3. **Timestamp visible**: Mostrar "Última actualización: YYYY-MM-DD HH:MM"
4. **Próxima actualización**: Mostrar "Próxima actualización: YYYY-MM-DD HH:MM"
5. **NO WebSockets/SSE**: Polling deshabilitado por diseño

---

## Roadmap

### v0.1.0 (Actual)
- Estructura base modular monolith
- Redux Toolkit configurado
- Webpack + Babel + Jest
- Módulo home de ejemplo
- Path aliases

### v0.2.0 (Próximo)
- Módulo de autenticación (login)
- Integración con API backend JWT
- Módulo de dashboard (10 widgets)
- Módulo de reportes

### v0.3.0 (Futuro)
- Módulo de alertas
- Módulo de exportaciones
- Módulo de administración usuarios
- Tests E2E con Playwright

---

## Documentación Adicional

### ADRs (Architecture Decision Records)

- **ADR_011**: Modular Monolith vs Microfrontends
- **ADR_012**: Redux Toolkit vs Context API
- **ADR_013**: Webpack vs Vite
- **ADR_014**: Testing Strategy

Ver: `docs/adr/`

### Requisitos

- **N-001**: Visibilidad metricas IVR
- **RF-010**: Pantalla de login
- **RF-011**: Cambio de password UI
- **RF-012**: Dashboard con 10 widgets

Ver: `implementacion/frontend/requisitos/`

---

## Troubleshooting

### "Module not found" con path aliases

Verificar:
1. `webpack.config.cjs` tiene alias configurado
2. `package.json` jest.moduleNameMapper tiene alias
3. Reiniciar dev server

### Tests fallan con "Cannot find module '@app/...'"

Verificar `package.json` > jest > moduleNameMapper.

### Hot reload no funciona

Verificar `webpack.config.cjs` > devServer > hot: true.

---

## Contribuir

### Convenciones

1. **Componentes**: PascalCase (MyComponent.jsx)
2. **Hooks**: camelCase con prefijo use (useMyHook.js)
3. **Archivos de estado**: camelCase + Slice (mySlice.js)
4. **Tests**: Mismo nombre + .test.jsx/.test.js
5. **Módulos**: Un directorio por módulo en src/modules/

### Code Style

- ESLint: Pendiente configurar
- Prettier: Pendiente configurar
- Por ahora: Seguir estilo de archivos existentes

---

**Versión**: 0.1.0
**Última actualización**: 2025-11-06
**Contacto**: Equipo Frontend
