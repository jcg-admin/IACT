#!/bin/bash

# Lista de dominios a verificar
DOMINIOS=(
  "postgresql.org"
  "apt.postgresql.org"
  "www.postgresql.org"
)

echo "Verificando resolución DNS y conectividad..."

for dominio in "${DOMINIOS[@]}"; do
  echo ""
  echo "Dominio: $dominio"

  echo "nslookup:"
  nslookup "$dominio"

  echo "ping (5 segundos):"
  ping -w 5 "$dominio"
done

echo ""
echo "Verificación completada."
