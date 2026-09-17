# Informe de Conciliación Documental (Gap Analysis)
**Proyecto:** TicketHelp — Auditoría de Ingeniería Inversa y Aseguramiento de la Calidad
**Estudiante:** María José López Reyes (Código: 1152268)
**Asignatura:** Gestión y Aseguramiento de la Calidad en Proyectos de Software — UFPS (2026-II)
**Norma de referencia:** ISO/IEC 25010 (calidad del producto) e ISO/IEC/IEEE 29119 (procesos de prueba)
**Alcance:** `tickethelp-backend/` y `tickethelp-frontend/` (inspección estática, sin modificación de código)

## 1. Nota de trazabilidad documental

La conciliación de esta sección se realizó contrastando el código fuente auditado contra el documento de requerimientos e historias de usuario del proyecto (`_audit_docs/REQUERIMIENTOS_Y_HC.md`), en particular el requisito no funcional RNF-06 (Mantenibilidad, que exige pruebas automatizadas básicas) y las historias de usuario que documentan la política de acceso `IsAdmin` para los endpoints administrativos, incluida la HU13 (Historial de ticket). Dicha revisión confirma, sin introducir hallazgos adicionales, la intención documentada ya referenciada en los comentarios de `reports/urls.py` y refuerza la trazabilidad de la no conformidad GAP-04.

## 2. Matriz de no conformidades verificadas

| # | Componente | Requisito / Intención documentada | Implementación real (evidencia) | Severidad | Plan de mitigación |
|---|---|---|---|---|---|
| GAP-01 | `tickethelp-frontend/package.json` | Proyecto declarado y construido sobre Vite (`vite.config.js`, scripts `dev`/`build` vía `vite`) | La dependencia `"next": "^15.5.15"` está declarada en `dependencies` sin ningún uso: no existe `next.config.*`, ni carpeta `pages/`/`app/`, ni imports de `next` en `src/`. Es una dependencia huérfana que infla el árbol de instalación y el `package-lock.json`. | Baja | Retirar `next` de `package.json` con `npm uninstall next` y regenerar el lockfile; validar que `npm run build` no se vea afectado. |
| GAP-02 | `tickethelp-frontend/.env` + `src/api/client.js`, `src/api/clienteApi.js`, `src/lib/api.js` | Configurar dinámicamente la URL base del backend consumido por Axios/fetch | (a) `.env` define `VITE_BACKEND_URL=https:tickethelp-backend.onrender.com`, sin el separador `//`; `new URL(...)` sobre ese valor lanza `TypeError` (reproducido en la prueba `FE-RES-01b`). (b) Ninguno de los tres clientes HTTP del frontend lee `VITE_BACKEND_URL`: los tres leen `import.meta.env.VITE_API_URL`, variable que **no existe** en `.env`. Es decir, la variable de entorno configurada está completamente huérfana y el cliente siempre cae al valor por defecto `http://localhost:8000`, incluso en despliegue. | Alta | Unificar el nombre de la variable (`VITE_API_URL`) entre `.env` y el código fuente, corregir el valor con el esquema completo (`https://...`) y agregar una validación de arranque (`new URL()`) que falle rápido si la variable es inválida. |
| GAP-03 | `tickethelp-backend/tickets/views.py` (HU13B — Historial de ticket) | Una única vista `TicketHistoryAV` que resuelva `GET /api/tickets/<id>/history/` | La clase `TicketHistoryAV` está **definida dos veces** en el mismo módulo (líneas 563 y 760). Por resolución de nombres de Python, la segunda definición sobrescribe a la primera; la definición de la línea 563 queda inalcanzable (código muerto) y únicamente la de la línea 760 —con lógica adicional de resolución de usuario por `user_document`— es la efectivamente enrutada. Ambas declaran `permission_classes = [IsAdmin]`, por lo que el endpoint sí exige rol administrador, pero la duplicación viola el principio de fuente única de verdad y constituye un riesgo de mantenimiento (un cambio futuro en la primera definición no tendría efecto alguno). | Media | Eliminar la definición muerta (línea 563-607) y conservar una sola implementación documentada; agregar una prueba de regresión que falle si el módulo vuelve a declarar la clase más de una vez. |
| GAP-04 | `tickethelp-backend/reports/urls.py` (comentarios "solo administradores") | Todas las rutas bajo `stats/*` restringidas a rol ADMIN | De las 14 vistas de `reports/views.py`, **4 no declaran `permission_classes` propio**: `TicketAgingTopView` (`stats/aging-top/`), `TTATotalView` (`stats/tta/total/`), `ActiveClientsMonthlyComparisonView` (`stats/clientes-activos-mes/`) y `WeekdayResolutionCountView` (`stats/resolutions-by-weekday/`). Al no declararlo, heredan únicamente el default global `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` (`tickethelp/settings.py:209-211`), sin verificación de rol. Confirmado empíricamente: usuarios con rol `CLIENT` y `TECH` obtienen `200 OK` en estas 3 rutas verificadas por prueba automatizada (`SEC-01`), en contraste con `GeneralStatsView`, que sí exige `IsAdmin` y responde `403`. | Alta | Añadir `permission_classes = [IsAdmin]` a las 4 vistas identificadas; incorporar una prueba de humo que recorra `reports/urls.py` y verifique que toda vista bajo `stats/` distinta de `stats/performance/` (uso técnico) declare `IsAdmin`. |
| GAP-05 | `tickethelp-frontend/src/**` (manejo de errores de API) | Retroalimentación consistente al usuario ante fallos de backend (401/403/500) | Se identificaron 3 implementaciones de cliente HTTP con lógica de extracción de error distinta entre sí (`src/api/client.js`, `src/api/clienteApi.js`, `src/lib/api.js`) y 18 archivos en `src/` que capturan errores únicamente con `console.error(...)` sin normalizar el mensaje hacia la interfaz de usuario (`src/pages/tecnico/page.jsx`, `TicketsAsignados.jsx`, `TechnicianPerformanceDashboard.jsx`, `NotificationsPage.jsx`, `tickets_cliente.jsx`, `TicketTimelineModal.jsx`, `AuthContext.jsx`, `VisualizarTickets.jsx`, `UserPage.jsx`, `Reportes.jsx`, `GestionarTickets.jsx`, `Configuracion.jsx`, `useChangeHistory.js`, `TicketApprovalModal.jsx`, `AttachmentsGalleryModal.jsx`, `user2.js`, `client.js`, `api.js`). | Media | Consolidar en un único cliente HTTP (retirar los dos clientes redundantes) y centralizar la normalización de `detail`/`message`/`error` en un solo punto, propagando el mensaje a un componente de notificación visible en vez de sólo a consola. |

## 3. Hallazgos del brief de auditoría verificados como NO reproducibles

Por rigor técnico, se deja constancia de que las siguientes presunciones del alcance original de auditoría **fueron inspeccionadas y no se confirmaron** en el estado actual del código (evitando así reportar no conformidades no evidenciadas):

| Presunción original | Evidencia de inspección real |
|---|---|
| Omisión de `sendgrid` en `requirements.txt` | `sendgrid==6.11.0` está presente en `tickethelp-backend/requirements.txt` (línea final del archivo). |
| Migración `0007_create_default_estados.py` con riesgo de `IntegrityError` por inserciones no idempotentes | La migración usa `Estado.objects.get_or_create(codigo=..., defaults={...})` para las 5 filas, patrón idempotente que no falla ante reejecución. |
| Endpoint `/api/tickets/<id>/history/` con política `AllowAny` | La vista activa (`TicketHistoryAV`, línea 760 de `tickets/views.py`) declara `permission_classes = [IsAdmin]` y fue verificada por prueba automatizada (`SEC-03`) devolviendo `401`/`403` según corresponda. El hallazgo real relacionado con esta vista es la duplicación de clase documentada en **GAP-03**, no una política de permisos abierta. |

## 4. Trazabilidad hacia el banco de pruebas

| No conformidad | Caso(s) de prueba que la evidencian |
|---|---|
| GAP-02 | FE-RES-01, FE-RES-01b, FE-RES-01c |
| GAP-04 | SEC-01 |
| GAP-03 / verificación de permisos activos | SEC-02, SEC-03 |
| Resiliencia general del cliente (relacionado con GAP-05) | FE-RES-02, FE-RES-03 |
| Integridad de serializers (no listada como no conformidad, control de calidad positivo) | CB-01, CB-02, CB-03 |
