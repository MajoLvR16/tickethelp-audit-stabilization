"""
FASE 3 - Pruebas de caja negra: seguridad RBAC y resiliencia.
Endpoints auditados en tickethelp-backend/reports/urls.py, tickethelp-backend/
reports/views.py, tickethelp-backend/tickets/urls.py, tickethelp-backend/
tickets/views.py y tickethelp-backend/users/urls.py (solo lectura).

Nota de auditoría (ver _audit_docs/GAP_ANALYSIS_INFORME.md, GAP-04):
/api/reports/stats/aging-top/, /api/reports/stats/tta/total/,
/api/reports/stats/clientes-activos-mes/ y
/api/reports/stats/resolutions-by-weekday/ eran vistas APIView de
reports/views.py que NO declaraban permission_classes propio y por lo tanto
heredaban únicamente el default global IsAuthenticated
(tickethelp/settings.py:209-211), sin restricción de rol ADMIN. Remediado en
CR-01 (permission_classes = [IsAdmin] agregado a las 4 vistas); estos tests
ahora verifican la ausencia de regresión sobre esa corrección, no un
hallazgo pendiente.
"""
import pytest

pytestmark = pytest.mark.django_db

RUTAS_ADMIN_SIN_RESTRICCION_DE_ROL = [
    "/api/reports/stats/aging-top/",
    "/api/reports/stats/tta/total/",
    "/api/reports/stats/clientes-activos-mes/",
    "/api/reports/stats/resolutions-by-weekday/",
]


class TestSEC01RestriccionRutasAdministrativas:
    """SEC-01: rutas de estadísticas administrativas frente a perfiles
    CLIENT y TECH."""

    @pytest.mark.parametrize("ruta", RUTAS_ADMIN_SIN_RESTRICCION_DE_ROL)
    def test_regresion_cliente_no_accede_a_stats_administrativas(self, client_client, ruta):
        """Verifica ausencia de regresión de CR-01: el cliente autenticado
        debe recibir 403, ya que las 4 vistas declaran
        permission_classes = [IsAdmin]."""
        response = client_client.get(ruta)
        assert response.status_code == 403

    @pytest.mark.parametrize("ruta", RUTAS_ADMIN_SIN_RESTRICCION_DE_ROL)
    def test_regresion_tecnico_no_accede_a_stats_administrativas(self, tech_client, ruta):
        """Verifica ausencia de regresión de CR-01: el técnico autenticado
        debe recibir 403, ya que las 4 vistas declaran
        permission_classes = [IsAdmin]."""
        response = tech_client.get(ruta)
        assert response.status_code == 403

    def test_ruta_general_stats_si_esta_correctamente_protegida(self, client_client):
        """Control de referencia: GeneralStatsView SÍ declara
        permission_classes = [IsAdmin] (reports/views.py:42) y responde 403."""
        response = client_client.get("/api/reports/stats/general-stats/")
        assert response.status_code == 403

    def test_ruta_general_stats_admin_obtiene_200(self, admin_client):
        response = admin_client.get("/api/reports/stats/general-stats/")
        assert response.status_code == 200


class TestSEC02DenegacionAprobacionTicketsCriticos:
    """SEC-02: /api/tickets/testing-approval/<id>/ debe denegar la
    aprobación de pruebas a usuarios no administradores (IsAdmin,
    tickets/views.py:344). La verificación de permiso ocurre en el
    dispatch antes de resolver el objeto, por lo que un ticket_id
    inexistente igualmente debe responder 403 para un perfil no admin."""

    def test_cliente_no_puede_aprobar_ticket(self, client_client, sample_ticket):
        response = client_client.patch(
            f"/api/tickets/testing-approval/{sample_ticket.pk}/",
            {"action": "approve"},
            format="json",
        )
        assert response.status_code == 403

    def test_tecnico_no_puede_aprobar_ticket(self, tech_client, sample_ticket):
        response = tech_client.patch(
            f"/api/tickets/testing-approval/{sample_ticket.pk}/",
            {"action": "approve"},
            format="json",
        )
        assert response.status_code == 403

    def test_no_autenticado_no_puede_aprobar_ticket(self, anon_client, sample_ticket):
        response = anon_client.patch(
            f"/api/tickets/testing-approval/{sample_ticket.pk}/",
            {"action": "approve"},
            format="json",
        )
        assert response.status_code == 401


class TestSEC03RechazoTokenMalformadoOExpirado:
    """SEC-03: /api/tickets/<id>/history/ debe rechazar Bearer tokens
    malformados con 401 (tickets/views.py:760-820, IsAdmin +
    JWTAuthentication)."""

    def test_token_malformado_retorna_401(self, anon_client, sample_ticket):
        anon_client.credentials(HTTP_AUTHORIZATION="Bearer token.invalido.no-jwt")
        response = anon_client.get(f"/api/tickets/{sample_ticket.pk}/history/")
        assert response.status_code == 401

    def test_token_con_firma_alterada_retorna_401(self, admin_client, sample_ticket):
        response = admin_client.get(f"/api/tickets/{sample_ticket.pk}/history/")
        original_auth = response.wsgi_request.META.get("HTTP_AUTHORIZATION", "")
        assert original_auth  # token legítimo emitido por fixture

        admin_client.credentials(HTTP_AUTHORIZATION=original_auth[:-4] + "abcd")
        response_alterada = admin_client.get(f"/api/tickets/{sample_ticket.pk}/history/")
        assert response_alterada.status_code == 401

    def test_sin_token_retorna_401(self, anon_client, sample_ticket):
        response = anon_client.get(f"/api/tickets/{sample_ticket.pk}/history/")
        assert response.status_code == 401


class TestSEC04ResilienciaDoSPayloadLogin:
    """SEC-04: /api/users/auth/login/ debe permanecer resiliente ante un
    payload de 5 MB inyectado en el campo email, respondiendo 400/401 sin
    colapsar en un error 500."""

    def test_payload_email_5mb_no_produce_error_500(self, anon_client):
        payload_email_masivo = "a" * (5 * 1024 * 1024) + "@test.com"
        response = anon_client.post(
            "/api/users/auth/login/",
            {"email": payload_email_masivo, "password": "cualquiera"},
            format="json",
        )
        assert response.status_code in (400, 401)

    def test_payload_email_5mb_no_password_sigue_siendo_400(self, anon_client):
        payload_email_masivo = "b" * (5 * 1024 * 1024)
        response = anon_client.post(
            "/api/users/auth/login/",
            {"email": payload_email_masivo},
            format="json",
        )
        assert response.status_code in (400, 401)
