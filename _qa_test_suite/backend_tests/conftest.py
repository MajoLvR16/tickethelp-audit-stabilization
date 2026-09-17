"""
Fixtures compartidos para el arnés de pruebas QA (backend).
Aislado de tickethelp-backend/: no modifica ni depende de datos de producción.
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def estado_open(db):
    from tickets.models import Estado
    estado, _ = Estado.objects.get_or_create(
        codigo="open", defaults={"nombre": "Abierto", "es_final": False}
    )
    return estado


@pytest.fixture
def estado_trial(db):
    from tickets.models import Estado
    estado, _ = Estado.objects.get_or_create(
        codigo="trial", defaults={"nombre": "Pruebas", "es_final": False}
    )
    return estado


@pytest.fixture
def estado_finalized(db):
    from tickets.models import Estado
    estado, _ = Estado.objects.get_or_create(
        codigo="finalized", defaults={"nombre": "Finalizado", "es_final": True}
    )
    return estado


@pytest.fixture
def admin_user(db):
    from users.models import Admin
    user, _ = Admin.objects.get_or_create(
        document="9100000001",
        defaults={"email": "qa.admin@test.com", "first_name": "QA", "last_name": "Admin"},
    )
    user.set_password("QaAdmin123*")
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def tech_user(db):
    from users.models import Technician
    user, _ = Technician.objects.get_or_create(
        document="9100000002",
        defaults={"email": "qa.tech@test.com", "first_name": "QA", "last_name": "Tech"},
    )
    user.set_password("QaTech123*")
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def client_user(db):
    from users.models import Client
    user, _ = Client.objects.get_or_create(
        document="9100000003",
        defaults={"email": "qa.client@test.com", "first_name": "QA", "last_name": "Client"},
    )
    user.set_password("QaClient123*")
    user.is_active = True
    user.save()
    return user


def _auth_client(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def admin_client(admin_user):
    return _auth_client(admin_user)


@pytest.fixture
def tech_client(tech_user):
    return _auth_client(tech_user)


@pytest.fixture
def client_client(client_user):
    return _auth_client(client_user)


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def sample_ticket(db, admin_user, tech_user, client_user, estado_open):
    from tickets.models import Ticket
    return Ticket.objects.create(
        administrador=admin_user,
        tecnico=tech_user,
        cliente=client_user,
        estado=estado_open,
        titulo="Ticket QA de prueba",
        descripcion="Generado por el arnés de auditoría QA",
        equipo="Laptop QA-01",
    )
