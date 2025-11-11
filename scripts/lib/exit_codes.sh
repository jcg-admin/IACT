#!/bin/bash
# Exit codes estandarizados para todos los scripts
# Constitution Rule 2: Exit codes consistency

# Exit codes principales
export EXIT_SUCCESS=0      # Validación pasó sin issues
export EXIT_FAIL=1         # Validación falló (bloquea CI/CD)
export EXIT_WARNING=2      # Warnings encontrados (no bloquea)

# Exit codes específicos (opcionales, para debugging)
export EXIT_INVALID_ARGS=10    # Argumentos inválidos
export EXIT_FILE_NOT_FOUND=11  # Archivo no encontrado
export EXIT_PERMISSION=12      # Permiso denegado
export EXIT_TIMEOUT=13         # Timeout excedido
