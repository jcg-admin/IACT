# Matriz de Trazabilidad Vertical
**Dominio:** BACK
**Generado:** 2025-11-17 09:52:21

Esta matriz muestra la cadena de trazabilidad vertical desde reglas de negocio hasta atributos de calidad.

## Estadísticas

| Tipo | Cantidad |
|------|----------|
| RN | 1 |
| RNEG | 1 |
| UC | 1 |
| RF | 1 |
| RNF | 1 |

## Matriz de Relaciones

| RN | RNEG | UC | RF | RNF |
|----|------|----|----|-----|
| RN-BACK-001 | RNEG-BACK-001 | UC-BACK-001 | RF-BACK-010 | RNF-BACK-005 |

## Detalles de Artefactos

### RN

**RN-BACK-001**: Usuario Debe Estar Autenticado
  - Referencias: RF-BACK-010, RF-BACK-011, RNEG-BACK-001, RNF-BACK-005, RNF-BACK-007, UC-BACK-001, UC-BACK-003
  - Referenciado por: RF-BACK-010, RNEG-BACK-001, RNF-BACK-005, UC-BACK-001

### RNEG

**RNEG-BACK-001**: Sistema de Autenticación Seguro
  - Referencias: RN-BACK-001, RN-BACK-002, UC-BACK-001, UC-BACK-002, UC-BACK-003, UC-BACK-004
  - Referenciado por: RN-BACK-001, UC-BACK-001

### UC

**UC-BACK-001**: Iniciar Sesión
  - Referencias: RF-BACK-010, RF-BACK-011, RF-BACK-012, RN-BACK-001, RN-BACK-028, RNEG-BACK-001, RNF-BACK-005, RNF-BACK-006, RNF-BACK-007
  - Referenciado por: RF-BACK-010, RN-BACK-001, RNEG-BACK-001, RNF-BACK-005

### RF

**RF-BACK-010**: Validar Credenciales contra Base de Datos
  - Referencias: RN-BACK-001, RNF-BACK-006, UC-BACK-001
  - Referenciado por: RN-BACK-001, UC-BACK-001

### RNF

**RNF-BACK-005**: Contraseña Mínimo 8 Caracteres
  - Referencias: RF-BACK-015, RN-BACK-001, UC-BACK-001, UC-BACK-003, UC-BACK-004
  - Referenciado por: RN-BACK-001, UC-BACK-001
