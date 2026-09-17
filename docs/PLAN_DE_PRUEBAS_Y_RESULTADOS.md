# Plan de Pruebas y Resultados
**Norma de referencia:** ISO/IEC/IEEE 29119 (partes 2 y 3 — procesos y documentación de prueba)
**Proyecto:** TicketHelp | **Estudiante:** María José López Reyes (1152268)
**Entorno de ejecución:** `_qa_test_suite/venv_qa` (Python 3.11, pytest 9.1.1, pytest-django 4.14.0) para backend; Node.js 22 (`node:test` nativo) para frontend. Suite aislada del código fuente auditado, sin dependencias añadidas al repositorio productivo.

## 1. Objetivo del plan

Verificar, mediante evidencia ejecutable y reproducible, el comportamiento de los componentes críticos de seguridad (RBAC), integridad de datos (serializers) y resiliencia de cliente (frontend) de TicketHelp, conforme a los hallazgos de la Fase 1 de auditoría estática (ver [`GAP_ANALYSIS_INFORME.md`](GAP_ANALYSIS_INFORME.md)).

## 2. Alcance

- **Dentro de alcance:** `tickets/serializers.py`, `users/serializers.py`, endpoints de `reports/`, `tickets/` y `users/` expuestos vía DRF; clientes HTTP del frontend (`src/api/client.js`, `src/lib/api.js`, `src/api/clienteApi.js`) y configuración de entorno (`.env`).
- **Fuera de alcance:** pruebas de interfaz gráfica end-to-end, pruebas de carga/rendimiento, pruebas de los módulos `notifications/` (fuera del alcance funcional solicitado).

## 3. Estrategia y trazabilidad de identificadores

| Prefijo | Tipo de prueba | Técnica | Archivo |
|---|---|---|---|
| CB-xx | Caja blanca | Análisis de código interno de serializers | `_qa_test_suite/backend_tests/test_serializers_white.py` |
| SEC-xx | Caja negra / seguridad | RBAC, autenticación JWT, resiliencia DoS | `_qa_test_suite/backend_tests/test_security_rbac.py` |
| FE-RES-xx | Caja negra / resiliencia | Simulación de respuestas HTTP y configuración | `_qa_test_suite/frontend_tests/test_client_resilience.mjs` |

## 4. Inventario de casos de prueba

### CB-01 — Validación de `TicketSerializer` ante payload vacío

| Campo | Detalle |
|---|---|
| Precondición | Ninguna (no requiere estado de base de datos). |
| Entrada | `TicketSerializer(data={})` |
| Aserción | `serializer.is_valid()` retorna `False`; `is_valid(raise_exception=True)` lanza `rest_framework.serializers.ValidationError`; las claves `administrador`, `tecnico`, `cliente`, `estado`, `titulo` están presentes en `serializer.errors`. |
| Comportamiento verificado | **APROBADO.** El serializer interrumpe la validación y reporta los 5 campos obligatorios faltantes, evidenciando que `fields = '__all__'` con `PrimaryKeyRelatedField(required=True)` funciona como control de integridad de entrada. |

### CB-02 — `UserUpdateSerializer`: exclusión de campos protegidos

| Campo | Detalle |
|---|---|
| Precondición | Usuario `CLIENT` existente (fixture `client_user`). |
| Entrada | Payload con `is_staff=True`, `is_superuser=True`, `role="ADMIN"` combinado con `first_name` legítimo. |
| Aserción | `UserUpdateSerializer.Meta.fields` no contiene `is_staff`/`is_superuser`/`role`; tras `serializer.save()`, el usuario persiste con `is_staff=False` y `role="CLIENT"`. |
| Comportamiento verificado | **APROBADO.** El whitelisting de campos (`fields = ['first_name', 'last_name', 'number']`) impide el escalamiento vertical de privilegios vía este serializer, incluso si el payload de entrada intenta inyectar los campos administrativos. |

### CB-03 — `UserCreateSerializer`: unicidad de email y documento

| Campo | Detalle |
|---|---|
| Precondición | Usuario `CLIENT` existente (`client_user`) con email y documento conocidos. |
| Entrada | (a) Payload con email duplicado; (b) payload con documento duplicado; (c) payload íntegramente único. |
| Aserción | Casos (a)/(b): `is_valid()` retorna `False` y la clave correspondiente (`email`/`document`) aparece en `serializer.errors`, **antes** de cualquier intento de `save()`. Caso (c): `is_valid()` retorna `True`. |
| Comportamiento verificado | **APROBADO.** La validación de unicidad ocurre en el método `validate()` del serializer (capa de aplicación), previo al `INSERT` en base de datos, previniendo un `IntegrityError` no controlado a nivel de motor de datos. |

### SEC-01 — Restricción de rutas administrativas de estadísticas

| Campo | Detalle |
|---|---|
| Precondición | Tokens JWT válidos para `CLIENT`, `TECH` y `ADMIN` (fixtures `client_client`, `tech_client`, `admin_client`). |
| Entrada | `GET` a `/api/reports/stats/aging-top/`, `/api/reports/stats/tta/total/`, `/api/reports/stats/clientes-activos-mes/` y, como control, `/api/reports/stats/general-stats/`. |
| Aserción | Documenta el estado real, no el esperado por diseño: `CLIENT`/`TECH` obtienen `200` en las 3 primeras rutas (no conformidad **GAP-04**); `CLIENT` obtiene `403` en `general-stats/` (control correctamente protegido); `ADMIN` obtiene `200` en todas. |
| Comportamiento verificado | **NO CONFORME (confirma GAP-04).** Las 3 rutas señaladas no aplican verificación de rol y son accesibles por cualquier usuario autenticado, contradiciendo la intención documentada en los comentarios de `reports/urls.py` ("solo administradores"). |

### SEC-02 — Denegación de aprobación de tickets críticos

| Campo | Detalle |
|---|---|
| Precondición | Ticket de prueba (`sample_ticket`) creado vía fixture con `Estado` obtenido por `get_or_create(codigo="open", ...)`. |
| Entrada | `PATCH /api/tickets/testing-approval/<id>/` con `{"action": "approve"}`, ejecutado con token `CLIENT`, token `TECH` y sin token. |
| Aserción | `CLIENT` → `403`; `TECH` → `403`; anónimo → `401`. |
| Comportamiento verificado | **APROBADO.** `TestingApprovalAV` (IsAdmin) rechaza correctamente a perfiles no administrativos antes de resolver el objeto o la lógica de negocio. |

### SEC-03 — Rechazo de token JWT malformado/expirado

| Campo | Detalle |
|---|---|
| Precondición | Ticket de prueba (`sample_ticket`); token admin legítimo emitido por fixture para el caso de firma alterada. |
| Entrada | `GET /api/tickets/<id>/history/` con: (a) cabecera `Bearer token.invalido.no-jwt`; (b) token admin válido con los últimos caracteres de la firma alterados; (c) sin cabecera `Authorization`. |
| Aserción | Los tres casos responden `401 Unauthorized`. |
| Comportamiento verificado | **APROBADO.** `JWTAuthentication` invalida correctamente tokens malformados, con firma alterada y ausentes, antes de alcanzar la capa de permisos `IsAdmin`. |

### SEC-04 — Resiliencia ante payload de 5 MB (DoS) en login

| Campo | Detalle |
|---|---|
| Precondición | Ninguna (endpoint público de autenticación). |
| Entrada | `POST /api/users/auth/login/` con el campo `email` de 5 MB (con y sin `password`). |
| Aserción | Código de respuesta en `{400, 401}`, explícitamente **no** `500`. |
| Comportamiento verificado | **APROBADO.** El límite `DATA_UPLOAD_MAX_MEMORY_SIZE` de Django (por defecto 2.5 MB, sin sobreescritura en `tickethelp/settings.py`) intercepta el payload sobredimensionado devolviendo `400` antes de que la vista lo procese; el servidor no colapsa con error `500`. |

### FE-RES-01 — Validación sintáctica de `VITE_BACKEND_URL`

| Campo | Detalle |
|---|---|
| Precondición | Lectura directa de `tickethelp-frontend/.env`. |
| Entrada | Valor real `VITE_BACKEND_URL=https:tickethelp-backend.onrender.com`. |
| Aserción | El valor debe cumplir `^https?:\/\/` y ser aceptado por `new URL(...)`. |
| Comportamiento verificado | **NO CONFORME (confirma GAP-02).** El valor actual carece de `//` y `new URL(...)` lanza `TypeError`, reproduciendo el defecto de configuración de forma determinista. Subcaso adicional (`FE-RES-01c`) confirma que, además, ningún cliente HTTP del frontend consume esta variable (lee `VITE_API_URL` en su lugar), por lo que el defecto es actualmente inerte en tiempo de ejecución pero bloqueante si se corrige sólo el nombre sin corregir el valor. |

### FE-RES-02 — Extracción de mensaje estructurado ante 401/403

| Campo | Detalle |
|---|---|
| Precondición | Cliente HTTP real (`src/api/client.js`) cargado en un entorno Node simulado (storage y `window` con shims mínimos, sin alterar el archivo fuente). |
| Entrada | Respuestas simuladas `403` con `{"detail": "..."}`, `401` con `{"detail": "..."}` y `403` sin cuerpo. |
| Aserción | `err.message` coincide con el texto de `detail` (nunca la cadena literal `"undefined"`); ante `401`, se limpian `localStorage`/`sessionStorage` y se redirige a `/auth/login`. |
| Comportamiento verificado | **APROBADO.** El cliente extrae correctamente el mensaje estructurado del backend y ejecuta la política de expiración de sesión sin lanzar excepciones no controladas. |

### FE-RES-03 — Timeouts y caídas 500

| Campo | Detalle |
|---|---|
| Precondición | Igual que FE-RES-02. |
| Entrada | (a) Respuesta `500` con cuerpo JSON; (b) `fetch` que nunca resuelve (servidor caído), acotado externamente con `Promise.race` a 200 ms; (c) `fetch` que rechaza con `TypeError` (fallo de red). |
| Aserción | (a) el error propagado conserva `status === 500`; (b) la promesa se rechaza por el timeout externo sin colgar el proceso de prueba; (c) el `TypeError` se propaga sin ser silenciado. |
| Comportamiento verificado | **APROBADO.** El cliente no captura ni enmascara errores de red o de servidor; los propaga como excepciones `Error` con metadatos (`status`, `data`), permitiendo a las 18 pantallas identificadas en **GAP-05** manejarlos (aunque hoy sólo lo hagan vía `console.error`). |

## 5. Resumen de ejecución (evidencia real, no proyectada)

| Suite | Casos | Aprobados | No conformes (defecto confirmado) | Comando de ejecución |
|---|---|---|---|---|
| Backend (`pytest`) | 23 (agrupados en CB-01..03, SEC-01..04) | 23/23 assertions programadas se ejecutan según diseño (SEC-01 documenta intencionalmente el estado NO CONFORME de GAP-04 como resultado esperado de la prueba, no como fallo de ejecución) | — | Ver sección 6 |
| Frontend (`node:test`) | 9 (FE-RES-01, 01b, 01c, 02, 02b, 02c, 03a, 03b, 03c) | 7/9 | 2/9 (FE-RES-01, FE-RES-01b — reproducen GAP-02 de forma determinista) | Ver sección 6 |

## 6. Comandos de ejecución determinista

**Backend con cobertura (PowerShell):**
```powershell
cd _qa_test_suite
.\venv_qa\Scripts\python.exe -m pytest backend_tests/ -v --cov=tickets --cov=users --cov=reports --cov-report=term-missing --cov-report=html:reports/coverage_html
```

**Frontend (PowerShell, requiere Node.js 22+):**
```powershell
cd _qa_test_suite
node --test frontend_tests/test_client_resilience.mjs
```

Cobertura de línea medida sobre `tickets/`, `users/` y `reports/` (aplicaciones bajo prueba, excluidas migraciones y suites preexistentes no ejecutadas por este arnés): **36 % (1319/2046 líneas no cubiertas)**, reportada en `_qa_test_suite/reports/coverage_html/index.html`. Se documenta como línea base del banco de pruebas incorporado por esta auditoría; no sustituye una meta de cobertura institucional, la cual debería definirse en el SRS ausente (ver sección 1 del Gap Analysis).
