"""Servicios para presupuestos."""

import json
from typing import List
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Presupuesto

User = get_user_model()


class PresupuestoService:
    
    @staticmethod
    def crear_presupuesto(titulo, descripcion, monto, periodo_inicio, periodo_fin, creado_por_id):
        usuario = User.objects.get(id=creado_por_id)
        return Presupuesto.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            monto=monto,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            creado_por=usuario,
            estado='borrador'
        )
    
    @staticmethod
    def listar_presupuestos(estado=None):
        qs = Presupuesto.objects.all()
        if estado:
            qs = qs.filter(estado=estado)
        return list(qs)
    
    @staticmethod
    def aprobar_presupuesto(presupuesto_id, aprobado_por_id):
        presupuesto = Presupuesto.objects.get(id=presupuesto_id)
        usuario = User.objects.get(id=aprobado_por_id)
        
        if presupuesto.estado != 'pendiente':
            raise ValidationError('Solo se pueden aprobar presupuestos pendientes')
        
        presupuesto.estado = 'aprobado'
        presupuesto.aprobado_por = usuario
        presupuesto.save()
        return presupuesto
    
    @staticmethod
    def rechazar_presupuesto(presupuesto_id, rechazado_por_id):
        presupuesto = Presupuesto.objects.get(id=presupuesto_id)
        usuario = User.objects.get(id=rechazado_por_id)
        
        if presupuesto.estado != 'pendiente':
            raise ValidationError('Solo se pueden rechazar presupuestos pendientes')
        
        presupuesto.estado = 'rechazado'
        presupuesto.aprobado_por = usuario
        presupuesto.save()
        return presupuesto
    
    @staticmethod
    def exportar_presupuestos():
        presupuestos = Presupuesto.objects.all()
        data = [
            {
                'id': p.id,
                'titulo': p.titulo,
                'monto': str(p.monto),
                'estado': p.estado,
                'periodo_inicio': p.periodo_inicio.isoformat(),
                'periodo_fin': p.periodo_fin.isoformat()
            }
            for p in presupuestos
        ]
        return json.dumps(data, indent=2)
