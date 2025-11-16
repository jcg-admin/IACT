---
id: DOC-MOBILE-PROMPTS
estado: activo
propietario: equipo-mobile
ultima_actualizacion: 2025-11-14
relacionados:
  - DOC-PROMPT-ENGINEERING
  - DOC-CLAUDE-ADVANCED-TECHNIQUES
  - DOC-AI-INDEX
  - DOC-FRONTEND-UI-PROMPTS
date: 2025-11-14
---
# Ejemplos avanzados de prompting para desarrollo mobile (Android · iOS · React Native · Flutter)

Esta guía reúne prompts especializados para acelerar el delivery mobile del call center, aplicando los lineamientos de **Técnicas Avanzadas Específicas para Claude** y el catálogo de **Técnicas Avanzadas de Prompt Engineering**. Todos los bloques enfatizan prevención de alucinaciones (definidas como "información plausible pero incorrecta" como fechas, APIs inexistentes o código sutilmente erróneo) mediante validaciones cruzadas, cadenas de verificación y métricas de éxito claras.

## Principios rectores

1. **Roles explícitos**: Encapsula expertise (Android lead, iOS architect, React Native specialist, Flutter tech lead) para forzar respuestas en contexto.
2. **Cadena Auto-CoT + Self-Consistency**: Solicita al menos dos rutas de razonamiento y síntesis final para reducir desvíos.
3. **Validaciones anti-alucinación**: Exige listas de "hechos confirmados", "supuestos" y "datos que requieren verificación" en cada salida.
4. **Cláusulas Claude**: Usa context windows amplios (hasta 200K) para adjuntar specs completas, pero limita temperatura ≤0.3 para entregables compilables. Invoca "Técnicas Avanzadas Específicas para Claude" cuando necesites razonar sobre artifacts largos o llamadas MCP.
5. **Meta-prompts encadenados**: Antes de usar un prompt productivo, ejecuta `Generador Universal de Prompts` → `Evaluador Automático` → `Generador de Prompts Anti-Alucinación` del `META_PROMPTS_LIBRARY.md` para auditar calidad.

## Plantilla base modular

```text
<ProjectLayout>
Contexto del módulo mobile (release, dependencias, APIs).
</ProjectLayout>

<Goals>
- Objetivos claros (feature, bugfix, PoC) y métricas (coverage ≥80 %, fps, consumo de batería).
</Goals>

<Limitations>
- Plataformas soportadas, conectividad, feature flags.
</Limitations>

<BuildInstructions>
- Comandos verificados (Gradle, Xcodebuild, Metro, Flutter test) y orden de ejecución.
</BuildInstructions>

<ProjectLayout>
- Carpetas relevantes (`android/app/src`, `ios/Runner`, `apps/mobile`).
</ProjectLayout>

<StepsToFollow>
1. Invocar meta-prompt adecuado.
2. Solicitar Auto-CoT + Self-Consistency.
3. Exigir checklist anti-alucinación.
4. Pedir formato estructurado (tabla Markdown/JSON) con campos: `Supuesto`, `Cómo validar`, `Deadline`.
</StepsToFollow>
```

## Secuencia recomendada de prompting

1. **Discovery**: Usa `Generador Universal de Prompts` para obtener contexto y objetivos multiplataforma.
2. **Diseño técnico**: Ejecuta `Generador de Prompts por Dominio Técnico` con dominio "Mobile cross-platform" para guiar arquitectura.
3. **Desarrollo**: Según plataforma, selecciona los prompts de este documento y combina con `Generador de Variaciones` para A/B testing.
4. **Validación**: Corre `Meta-Prompt para Generación de Prompts de Validación` para auditar respuestas (unit tests, UI tests, performance).
5. **Hardening**: Si detectas fallos, activa `Meta-Prompt para Debugging de Prompts` y `Optimizador Automático` antes de otro intento.

## Prompts especializados por plataforma

### Android (Kotlin · Jetpack Compose)

```text
Actúa como Android lead senior especializado en Jetpack Compose y arquitectura modular.
Contexto: Feature "Dashboard en vivo" para supervisores de call center (api/callcentersite, WebSocket + fallback REST).
Objetivo: Diseñar blueprint completo (pantallas, states, ViewModels, repositorios) manteniendo cobertura ≥80 % (JUnit + Compose testing).
Limitations: Device API 24+, modo offline, build Gradle catalogado en `android/gradle/libs.versions.toml`.
Técnicas Avanzadas Específicas para Claude: aplica lectura incremental de archivos largos, verifica referencias a librerías (`accompanist`, `paging3`), responde en bloques `<HighLevelDetails>`, `<BuildInstructions>`, `<ProjectLayout>`.
Prevención de alucinaciones: separa "Componentes confirmados" vs "Supuestos"; rechaza librerías inexistentes. Incluye plan para `./gradlew lintDebug testDebugUnitTest`.
Salida: Markdown con secciones [Arquitectura], [Estados + eventos], [Test Plan], [Riesgos de alucinación].
```

#### Prompt para artifacts Kotlin controlados

```text
Role: Android build engineer.
Solicito Artifact Kotlin con el ViewModel `LiveDashboardViewModel`.
Requisitos: Implementar `StateFlow`, manejo de WebSocket + fallback, inyección con Hilt.
Validación: generar bloque de pruebas `LiveDashboardViewModelTest` (JUnit + Turbine) y checklist para `./gradlew connectedDebugAndroidTest`.
Anti-alucinación: declara fuentes reales (`callsRepository`, `supervisorPreferences`) y marca cualquier endpoint dudoso.
```

### iOS (Swift · SwiftUI)

```text
Actúa como iOS architect senior con experiencia en SwiftUI y Combine.
Contexto: Implementar "Estado de agentes" para iPadOS y iOS.
Objetivo: Definir `AppIntent` para widgets, esquema de navegación y pruebas (XCTest + snapshot).
Limitations: iOS 15+, compatibilidad con MDM corporativo, sin API privadas.
Técnicas Avanzadas de Prompt Engineering: usa Auto-CoT + Tree-of-Thoughts para comparar estrategias MVVM vs The Composable Architecture.
Prevención de alucinaciones: exige listado de frameworks confirmados (`Combine`, `WidgetKit`), datos que requieren verificación y comandos `xcodebuild -scheme CallCenterApp -destination 'platform=iOS Simulator,name=iPhone 15' test`.
Salida: Tabla con columnas [Componente, Fuente de datos, Test, Riesgo].
```

#### Prompt anti-alucinación para widgets

```text
Role: iOS QA engineer.
TAREA CRÍTICA: Validar widget "AgentStatus".
Riesgo de alucinación: alto (datos en tiempo real).
Consecuencias: críticas (alertas erróneas a supervisores).
Estrategia: usa Meta-Prompt Anti-Alucinación → generar checklist con "Basándome en información verificable...", "No tengo datos confirmados sobre..." para cada métrica.
Formato: JSON con campos {fact, evidence, confidence, needs_verification}.
```

### React Native (TypeScript · Expo)

```text
Actúa como React Native specialist con foco en Expo + Reanimated 3.
Contexto: Migrar módulo "Agenda" para agentes de campo.
Objetivo: Diseñar prompts que produzcan hooks resilientes (`useOfflineAgenda`), navegación (React Navigation v7), pruebas (Jest + Detox) y métricas de performance.
Limitations: Soporte Android/iOS, sin módulos nativos propios, offline-first.
Técnicas Avanzadas Específicas para Claude: combina Auto-CoT con Chain-of-Verification para validar APIs (`expo-secure-store`, `expo-notifications`).
Anti-alucinación: obliga al LLM a listar dependencias confirmadas vs pendientes, incluir comandos `npx expo run:ios`, `npx expo run:android`, `npx detox test --configuration ios.sim.debug`.
Salida: Blueprint con secciones `<Goals>`, `<BuildInstructions>`, `<ProjectLayout>`, `<StepsToFollow>`.
```

#### Prompt para evitar código fantasma

```text
Role: RN code reviewer.
Analiza hook generado (`useOfflineAgenda.ts`).
Checklist: compatibilidad Hermes, manejo de AppState, sincronización con backend.
Meta-Prompt Evaluador: puntúa estructura, anti-alucinación, claridad, reproducibilidad y completitud (0-10).
Reporta tabla de riesgos y acciones de remediación.
```

### Flutter (Dart · Riverpod)

```text
Actúa como Flutter tech lead especializado en Riverpod 3 y Material 3.
Contexto: App "Supervisor Insight" multiplataforma.
Objetivo: Diseñar arquitectura clean con `FeatureFlags`, `StateNotifier`, theming y pruebas (widget + integración).
Limitations: Soporte web opcional, integración con `calls_service.proto`, build CI via `flutter test --coverage` y `flutter build ipa`.
Técnicas Avanzadas de Prompt Engineering: usa Tree-of-Thoughts para evaluar rutas (BLoC vs Riverpod) y Auto-CoT para justificar decisiones.
Anti-alucinación: separar "Dependencias confirmadas" (Flutter 3.24, Riverpod 3.0) de "Pendientes"; si se propone plugin inexistente, marcar "Requiere verificación adicional".
Salida: Documento con secciones [Arquitectura], [Diagrama textual], [Plan de pruebas], [Checklist anti-alucinación].
```

#### Prompt para pipelines Flutter

```text
Role: Mobile DevOps engineer.
Solicito script YAML para GitHub Actions que ejecute `flutter pub get`, `flutter analyze`, `flutter test --coverage`, `flutter build appbundle`.
Validaciones: asegurar caches correctos, manejo de claves, cobertura ≥80 %.
Meta-Prompt Variations: crea 5 variantes (especificidad, anti-alucinación, estructura, contexto, simplicidad) para comparar.
Plan de testing: definir métricas (tiempo, fallas, cobertura) y criterios de selección.
```

## Playbooks anti-alucinación

- **Definición operativa**: alucinaciones son respuestas plausibles pero incorrectas (citas falsas, código erróneo, referencias inventadas). Antes de aceptar un output, valida hechos, ejecuta pruebas y solicita fuentes.
- **Listas obligatorias**: Cada prompt debe producir secciones "Basándome en información verificable...", "No tengo datos confirmados sobre...", "Requiere verificación adicional..." y "Dentro de mi conocimiento actualizado hasta...".
- **Cross-check**: Verifica APIs contra documentación real (`api/`, `docs/backend/`, `docs/frontend/`). Si el LLM propone funciones no existentes, regresa el prompt usando el `Meta-Prompt para Debugging de Prompts Problemáticos`.
- **Revisión humana**: Registrar hallazgos en ADRs cuando la IA afecte arquitectura; ejecutar TDD (Red→Green→Refactor) antes de merge y garantizar coverage ≥80 %.

## Uso combinado de meta-prompts

1. **Generador Universal de Prompts**: establece contexto, formato y métricas.
2. **Optimizador Automático**: refina prompts y documenta tabla comparativa.
3. **Generador de Prompts Anti-Alucinación**: añade validaciones, niveles de confianza y frases de seguridad.
4. **Generador de Variaciones**: crea prompts alternos para pruebas A/B en cada plataforma.
5. **Evaluador Automático**: puntúa calidad y genera recomendaciones.
6. **Debugging de Prompts**: diagnostica fallos con causa raíz, corrige y define plan de validación.
7. **Meta-Prompt Multi-Modelo**: adapta prompts a Claude, ChatGPT y Gemini cuando se requiera portabilidad.
8. **Orquestador Automatizado**: aplica pipeline completo (generar → evaluar → optimizar → validar) antes de publicar en `docs/mobile`.
9. **Prompt de Validación**: crea auditores que revisen cada respuesta y bloquean contenido dudoso.

Siguiendo esta guía, cada agente o colaborador puede producir prompts robustos para Android, iOS, React Native y Flutter reutilizando las técnicas avanzadas del repositorio y mitigando las alucinaciones desde el primer intento.
