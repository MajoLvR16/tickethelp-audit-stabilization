"""
FASE 2 - Pruebas de caja blanca: lógica interna de serializers.
Ubicación de origen inspeccionada: tickethelp-backend/tickets/serializers.py,
tickethelp-backend/users/serializers.py (solo lectura, sin modificación).
"""
import pytest
from rest_framework import serializers as drf_serializers

pytestmark = pytest.mark.django_db


class TestCB01TicketSerializerPayloadVacio:
    """CB-01: TicketSerializer debe rechazar payload vacío con ValidationError
    y reportar los campos obligatorios faltantes (administrador, tecnico,
    cliente, estado son PrimaryKeyRelatedField required=True)."""

    def test_payload_vacio_lanza_validation_error(self):
        from tickets.serializers import TicketSerializer

        serializer = TicketSerializer(data={})

        assert serializer.is_valid() is False
        with pytest.raises(drf_serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_payload_vacio_reporta_campos_obligatorios_faltantes(self):
        from tickets.serializers import TicketSerializer

        serializer = TicketSerializer(data={})
        serializer.is_valid()

        campos_obligatorios = {"administrador", "tecnico", "cliente", "estado", "titulo"}
        assert campos_obligatorios.issubset(serializer.errors.keys())


class TestCB02UserUpdateSerializerEscalamientoPrivilegios:
    """CB-02: UserUpdateSerializer expone únicamente ['first_name', 'last_name',
    'number'] en Meta.fields, por lo que campos administrativos (is_staff,
    is_superuser, role) no pueden escalarse vía este serializer aunque se
    inyecten en el payload de entrada."""

    def test_meta_fields_excluye_campos_protegidos(self):
        from users.serializers import UserUpdateSerializer

        declared_fields = set(UserUpdateSerializer.Meta.fields)
        campos_protegidos = {"is_staff", "is_superuser", "role"}

        assert declared_fields.isdisjoint(campos_protegidos)

    def test_payload_con_campos_protegidos_no_los_persiste(self, client_user):
        from users.serializers import UserUpdateSerializer

        payload = {
            "first_name": "Nuevo",
            "is_staff": True,
            "is_superuser": True,
            "role": "ADMIN",
        }
        serializer = UserUpdateSerializer(instance=client_user, data=payload, partial=True)

        assert serializer.is_valid(), serializer.errors
        assert "is_staff" not in serializer.validated_data
        assert "is_superuser" not in serializer.validated_data
        assert "role" not in serializer.validated_data

        updated_user = serializer.save()
        assert updated_user.is_staff is False
        assert updated_user.role == "CLIENT"


class TestCB03UserCreateSerializerUnicidad:
    """CB-03: UserCreateSerializer.validate() rechaza, previo al guardado en BD,
    emails y documentos duplicados (tickethelp-backend/users/serializers.py:26-42)."""

    def test_rechaza_email_duplicado_antes_de_guardar(self, client_user):
        from users.serializers import UserCreateSerializer

        payload = {
            "document": "9200000099",
            "email": client_user.email,
            "role": "CLIENT",
            "first_name": "Duplicado",
            "last_name": "Email",
        }
        serializer = UserCreateSerializer(data=payload)

        assert serializer.is_valid() is False
        assert "email" in serializer.errors

    def test_rechaza_documento_duplicado_antes_de_guardar(self, client_user):
        from users.serializers import UserCreateSerializer

        payload = {
            "document": client_user.document,
            "email": "otro.correo@test.com",
            "role": "CLIENT",
            "first_name": "Duplicado",
            "last_name": "Documento",
        }
        serializer = UserCreateSerializer(data=payload)

        assert serializer.is_valid() is False
        assert "document" in serializer.errors

    def test_payload_unico_es_valido(self):
        from users.serializers import UserCreateSerializer

        payload = {
            "document": "9200000100",
            "email": "unico.qa@test.com",
            "role": "CLIENT",
            "first_name": "Unico",
            "last_name": "QA",
        }
        serializer = UserCreateSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
