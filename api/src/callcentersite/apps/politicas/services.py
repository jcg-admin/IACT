import json
from django.contrib.auth import get_user_model
from .models import Politica

User = get_user_model()


class PoliticaService:
    
    @staticmethod
    def crear_politica(titulo, contenido, creado_por_id):
        usuario = User.objects.get(id=creado_por_id)
        return Politica.objects.create(
            titulo=titulo,
            contenido=contenido,
            creado_por=usuario
        )
    
    @staticmethod
    def listar_politicas(estado=None):
        qs = Politica.objects.all()
        if estado:
            qs = qs.filter(estado=estado)
        return list(qs)
    
    @staticmethod
    def publicar_politica(politica_id, publicado_por_id):
        politica = Politica.objects.get(id=politica_id)
        usuario = User.objects.get(id=publicado_por_id)
        politica.estado = 'publicada'
        politica.publicado_por = usuario
        politica.save()
        return politica
    
    @staticmethod
    def archivar_politica(politica_id):
        politica = Politica.objects.get(id=politica_id)
        politica.estado = 'archivada'
        politica.save()
        return politica
    
    @staticmethod
    def nueva_version(politica_id, nuevo_contenido, creado_por_id):
        original = Politica.objects.get(id=politica_id)
        usuario = User.objects.get(id=creado_por_id)
        return Politica.objects.create(
            titulo=original.titulo,
            contenido=nuevo_contenido,
            version=original.version + 1,
            creado_por=usuario
        )
