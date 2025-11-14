"""
Tests para registro publico de usuarios.

Verifica que el endpoint de registro funciona correctamente
sin requerir autenticacion.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Tests para el endpoint de registro publico de usuarios."""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        # No autenticar cliente - el registro es publico

    def test_registro_exitoso(self):
        """
        POST /api/v1/register/ - Registro exitoso de usuario.

        Given datos validos de registro
        When POST a /api/v1/register/
        Then retorna 201 CREATED
          And usuario es creado en la base de datos
          And retorna datos del usuario (sin password)
        """
        # Arrange
        datos = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@test.com',
            'password': 'SecureP@ss123',
            'password_confirm': 'SecureP@ss123',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Usuario registrado exitosamente'
        assert response.data['user']['username'] == 'nuevo_usuario'
        assert response.data['user']['email'] == 'nuevo@test.com'
        assert 'password' not in response.data['user']

        # Verificar que el usuario existe en la BD
        user = User.objects.get(username='nuevo_usuario')
        assert user.email == 'nuevo@test.com'
        assert user.is_active is True
        assert user.check_password('SecureP@ss123')

    def test_registro_sin_autenticacion(self):
        """
        El endpoint de registro debe ser accesible sin autenticacion.

        Given cliente no autenticado
        When POST a /api/v1/register/ con datos validos
        Then retorna 201 CREATED (no 401 Unauthorized)
        """
        # Arrange
        datos = {
            'username': 'usuario_publico',
            'email': 'publico@test.com',
            'password': 'SecureP@ss123',
            'password_confirm': 'SecureP@ss123',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_registro_password_no_coinciden(self):
        """
        POST /api/v1/register/ - Error cuando passwords no coinciden.

        Given password y password_confirm diferentes
        When POST a /api/v1/register/
        Then retorna 400 BAD REQUEST
          And retorna mensaje de error
        """
        # Arrange
        datos = {
            'username': 'usuario_error',
            'email': 'error@test.com',
            'password': 'SecureP@ss123',
            'password_confirm': 'DiferenteP@ss456',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_registro_password_muy_corto(self):
        """
        POST /api/v1/register/ - Error cuando password es muy corto.

        Given password con menos de 8 caracteres
        When POST a /api/v1/register/
        Then retorna 400 BAD REQUEST
        """
        # Arrange
        datos = {
            'username': 'usuario_pass_corto',
            'email': 'corto@test.com',
            'password': 'short1',
            'password_confirm': 'short1',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_registro_username_duplicado(self):
        """
        POST /api/v1/register/ - Error cuando username ya existe.

        Given un usuario existente con username 'existente'
        When POST a /api/v1/register/ con username 'existente'
        Then retorna 400 BAD REQUEST
          And retorna mensaje de username duplicado
        """
        # Arrange
        User.objects.create_user(
            username='existente',
            email='existente@test.com',
            password='ExistenteP@ss123',
        )

        datos = {
            'username': 'existente',
            'email': 'nuevo@test.com',
            'password': 'NuevoP@ss123',
            'password_confirm': 'NuevoP@ss123',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_registro_email_duplicado(self):
        """
        POST /api/v1/register/ - Error cuando email ya existe.

        Given un usuario existente con email 'existente@test.com'
        When POST a /api/v1/register/ con email 'existente@test.com'
        Then retorna 400 BAD REQUEST
          And retorna mensaje de email duplicado
        """
        # Arrange
        User.objects.create_user(
            username='usuario_existente',
            email='existente@test.com',
            password='ExistenteP@ss123',
        )

        datos = {
            'username': 'nuevo_usuario',
            'email': 'existente@test.com',
            'password': 'NuevoP@ss123',
            'password_confirm': 'NuevoP@ss123',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_registro_campos_requeridos(self):
        """
        POST /api/v1/register/ - Error cuando faltan campos requeridos.

        Given datos incompletos
        When POST a /api/v1/register/
        Then retorna 400 BAD REQUEST
        """
        # Arrange - datos sin username
        datos = {
            'email': 'incompleto@test.com',
            'password': 'SecureP@ss123',
            'password_confirm': 'SecureP@ss123',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_registro_email_invalido(self):
        """
        POST /api/v1/register/ - Error cuando email tiene formato invalido.

        Given email con formato invalido
        When POST a /api/v1/register/
        Then retorna 400 BAD REQUEST
        """
        # Arrange
        datos = {
            'username': 'usuario_email_malo',
            'email': 'esto-no-es-un-email',
            'password': 'SecureP@ss123',
            'password_confirm': 'SecureP@ss123',
        }

        # Act
        response = self.client.post('/api/v1/register/', datos, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
