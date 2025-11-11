"""
Tests de integración para API REST de usuarios.

Verifica que los endpoints HTTP funcionan correctamente.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserAPIREST:
    """Tests de integración para API REST /api/v1/users/"""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        # Crear usuario admin autenticado
        self.admin = User.objects.create_user(
            username='admin.test',
            password='AdminP@ss123',
            email='admin@test.com',
            is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

    def test_api_crear_usuario_exitoso(self):
        """
        API: POST /api/v1/users/ - Crear usuario exitoso.

        Given usuario autenticado
        When POST a /api/v1/users/ con datos válidos
        Then retorna 201 CREATED
          And retorna datos del usuario creado
        """
        # Arrange
        datos = {
            'username': 'nuevo.api',
            'email': 'nuevo.api@test.com',
            'password': 'SecureP@ss123',
            'segment': 'GE'
        }

        # Act
        response = self.client.post('/api/v1/users/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'nuevo.api'
        assert response.data['email'] == 'nuevo.api@test.com'
        assert response.data['segment'] == 'GE'
        assert 'password' not in response.data  # No retorna password

    def test_api_listar_usuarios(self):
        """
        API: GET /api/v1/users/ - Listar usuarios.

        Given usuarios existentes
        When GET a /api/v1/users/
        Then retorna 200 OK
          And retorna lista de usuarios
        """
        # Arrange
        User.objects.create_user(
            username='user1', password='pass', email='user1@test.com'
        )
        User.objects.create_user(
            username='user2', password='pass', email='user2@test.com'
        )

        # Act
        response = self.client.get('/api/v1/users/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 2

    def test_api_filtrar_usuarios_por_segment(self):
        """
        API: GET /api/v1/users/?segment=VIP - Filtrar por segmento.

        Given usuarios con diferentes segmentos
        When GET con query param segment=VIP
        Then retorna solo usuarios VIP
        """
        # Arrange
        User.objects.create_user(
            username='vip1', password='pass', email='vip1@test.com', segment='VIP'
        )
        User.objects.create_user(
            username='ge1', password='pass', email='ge1@test.com', segment='GE'
        )

        # Act
        response = self.client.get('/api/v1/users/?segment=VIP')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert all(u['segment'] == 'VIP' for u in response.data)

    def test_api_obtener_usuario_especifico(self):
        """
        API: GET /api/v1/users/{id}/ - Obtener usuario.

        Given usuario existente
        When GET a /api/v1/users/{id}/
        Then retorna 200 OK
          And retorna datos del usuario
        """
        # Arrange
        usuario = User.objects.create_user(
            username='consulta',
            password='pass',
            email='consulta@test.com'
        )

        # Act
        response = self.client.get(f'/api/v1/users/{usuario.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == usuario.id
        assert response.data['username'] == 'consulta'

    def test_api_actualizar_usuario(self):
        """
        API: PATCH /api/v1/users/{id}/ - Actualizar usuario.

        Given usuario existente
        When PATCH con nuevo email
        Then retorna 200 OK
          And email es actualizado
        """
        # Arrange
        usuario = User.objects.create_user(
            username='update.test',
            password='pass',
            email='old@test.com'
        )

        # Act
        response = self.client.patch(
            f'/api/v1/users/{usuario.id}/',
            {'email': 'new@test.com'},
            format='json'
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'new@test.com'

        # Verificar en BD
        usuario.refresh_from_db()
        assert usuario.email == 'new@test.com'

    def test_api_bloquear_usuario(self):
        """
        API: POST /api/v1/users/{id}/bloquear/ - Bloquear usuario.

        Given usuario activo
        When POST a /bloquear/ con razón
        Then retorna 200 OK
          And usuario queda bloqueado
        """
        # Arrange
        usuario = User.objects.create_user(
            username='block.test',
            password='pass',
            email='block@test.com',
            is_locked=False
        )

        # Act
        response = self.client.post(
            f'/api/v1/users/{usuario.id}/bloquear/',
            {'razon': 'Violación de políticas'},
            format='json'
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'bloqueado exitosamente' in response.data['message'].lower()

        # Verificar en BD
        usuario.refresh_from_db()
        assert usuario.is_locked is True
        assert usuario.lock_reason == 'ADMIN_LOCK'

    def test_api_desbloquear_usuario(self):
        """
        API: POST /api/v1/users/{id}/desbloquear/ - Desbloquear usuario.

        Given usuario bloqueado
        When POST a /desbloquear/
        Then retorna 200 OK
          And usuario queda desbloqueado
        """
        # Arrange
        usuario = User.objects.create_user(
            username='unlock.test',
            password='pass',
            email='unlock@test.com',
            is_locked=True
        )

        # Act
        response = self.client.post(f'/api/v1/users/{usuario.id}/desbloquear/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

        # Verificar en BD
        usuario.refresh_from_db()
        assert usuario.is_locked is False

    def test_api_cambiar_contrasena(self):
        """
        API: POST /api/v1/users/{id}/cambiar_contrasena/ - Cambiar contraseña.

        Given usuario con contraseña
        When POST con contraseña actual y nueva
        Then retorna 200 OK
          And contraseña es actualizada
        """
        # Arrange
        usuario = User.objects.create_user(
            username='pass.test',
            password='OldP@ss123',
            email='pass@test.com'
        )

        # Act
        response = self.client.post(
            f'/api/v1/users/{usuario.id}/cambiar_contrasena/',
            {
                'contrasena_actual': 'OldP@ss123',
                'contrasena_nueva': 'NewP@ss456'
            },
            format='json'
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK

        # Verificar nueva contraseña funciona
        usuario.refresh_from_db()
        assert usuario.check_password('NewP@ss456')
        assert not usuario.check_password('OldP@ss123')

    def test_api_eliminar_usuario(self):
        """
        API: DELETE /api/v1/users/{id}/ - Eliminar usuario.

        Given usuario existente
        When DELETE a /api/v1/users/{id}/
        Then retorna 204 NO CONTENT
          And usuario es soft deleted
        """
        # Arrange
        usuario = User.objects.create_user(
            username='delete.test',
            password='pass',
            email='delete@test.com'
        )

        # Act
        response = self.client.delete(f'/api/v1/users/{usuario.id}/')

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar soft delete
        usuario.refresh_from_db()
        assert usuario.is_deleted is True
        assert usuario.is_active is False

    def test_api_error_crear_usuario_con_email_duplicado(self):
        """
        API: POST /api/v1/users/ - Error con email duplicado.

        Given usuario existente con email
        When POST con mismo email
        Then retorna 400 BAD REQUEST
          And mensaje indica email duplicado
        """
        # Arrange
        User.objects.create_user(
            username='existing',
            password='pass',
            email='unique@test.com'
        )

        # Act
        response = self.client.post(
            '/api/v1/users/',
            {
                'username': 'new.user',
                'email': 'unique@test.com',  # Email duplicado
                'password': 'SecureP@ss123'
            },
            format='json'
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in str(response.data['error']).lower()

    def test_api_error_usuario_no_encontrado(self):
        """
        API: GET /api/v1/users/99999/ - Usuario no existe.

        When GET con ID inexistente
        Then retorna 404 NOT FOUND
        """
        # Act
        response = self.client.get('/api/v1/users/99999/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrado' in response.data['error'].lower()
