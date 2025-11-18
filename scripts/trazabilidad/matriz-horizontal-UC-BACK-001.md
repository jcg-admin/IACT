# Matriz de Trazabilidad: UC-BACK-001
**Título:** Iniciar Sesión
**Archivo:** UC-BACK-001-iniciar-sesion.md
**Generado:** 2025-11-17 09:52:29

Esta matriz muestra todos los artefactos relacionados con este elemento.

## Referencias Salientes

Artefactos referenciados por este elemento:

| ID | Tipo | Título |
|----|------|--------|
| RF-BACK-010 | RF | Validar Credenciales contra Base de Datos |
| RF-BACK-011 | ? | *(no encontrado)* |
| RF-BACK-012 | ? | *(no encontrado)* |
| RN-BACK-001 | RN | Usuario Debe Estar Autenticado |
| RN-BACK-028 | ? | *(no encontrado)* |
| RNEG-BACK-001 | RNEG | Sistema de Autenticación Seguro |
| RNF-BACK-005 | RNF | Contraseña Mínimo 8 Caracteres |
| RNF-BACK-006 | ? | *(no encontrado)* |
| RNF-BACK-007 | ? | *(no encontrado)* |

## Referencias Entrantes

Artefactos que referencian este elemento:

| ID | Tipo | Título |
|----|------|--------|
| RF-BACK-010 | RF | Validar Credenciales contra Base de Datos |
| RN-BACK-001 | RN | Usuario Debe Estar Autenticado |
| RNEG-BACK-001 | RNEG | Sistema de Autenticación Seguro |
| RNF-BACK-005 | RNF | Contraseña Mínimo 8 Caracteres |

## Árbol de Trazabilidad

### Cadena Ascendente (Por qué existe)

- **RN-BACK-001**: Usuario Debe Estar Autenticado
- **RNEG-BACK-001**: Sistema de Autenticación Seguro
  - **RN-BACK-001**: Usuario Debe Estar Autenticado

### Cadena Descendente (Qué implementa)

- **RF-BACK-010**: Validar Credenciales contra Base de Datos
- **RNF-BACK-005**: Contraseña Mínimo 8 Caracteres
