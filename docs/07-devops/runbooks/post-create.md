---
id: RB-DEVOPS-001
estado: borrador
propietario: equipo-devops
ultima_actualizacion: 2025-02-14
relacionados: ["DOC-OPS-001", "ADR-2025-001"]
---
# Runbook post-create de entorno Vagrant

1. **Crear o actualizar la VM**
   ```bash
   vagrant up
   ```
   Verifica que el aprovisionamiento termine sin errores críticos.
2. **Sincronizar dependencias de Django**
   ```bash
   vagrant ssh -- "cd /vagrant/api && pip install -r requirements.txt && pip install -r requirements-test.txt"
   ```
3. **Aplicar migraciones y colectar estáticos**
   ```bash
   vagrant ssh -- "cd /vagrant/api && python manage.py migrate && python manage.py collectstatic --noinput"
   ```
4. **Ejecutar chequeos rápidos**
   ```bash
   vagrant ssh -- "cd /vagrant/api && python manage.py check && pytest --maxfail=1"
   ```
   Si falla alguna prueba, etiqueta el incidente como `infra` y regístralo en el tablero de DevOps.
5. **Actualizar estado**
   Documenta fecha y responsable en `docs/07-devops/bitacora.md` (pendiente de crear) para mantener trazabilidad.
