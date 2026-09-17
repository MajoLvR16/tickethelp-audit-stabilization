# Auditoría de Gestión de la Configuración del Software (Sección 7)
**Proyecto:** TicketHelp | **Estudiante:** María José López Reyes (1152268)
**Referencia complementaria:** `_audit_docs/Auditoria Gestión de la Configuración- v2.md` (documento previo de la asignatura)
**Alcance:** Elementos de Configuración del Software (SCI) de `tickethelp-backend/` y `tickethelp-frontend/`, inspeccionados en modo lectura.

## 1. Propósito

Reportar, con evidencia trazable a archivo y línea, las no conformidades detectadas en los Elementos de Configuración del Software (dependencias declaradas, variables de entorno, artefactos de despliegue y consistencia entre módulos que gestionan el mismo recurso), como insumo para la Sección 7 del informe final de calidad.

## 2. Inventario de SCI auditados

| SCI | Ubicación | Función |
|---|---|---|
| Manifiesto de dependencias backend | `tickethelp-backend/requirements.txt` | Declara versiones fijas de librerías Python del backend Django. |
| Manifiesto de dependencias frontend | `tickethelp-frontend/package.json` | Declara dependencias npm del cliente React/Vite. |
| Variables de entorno frontend | `tickethelp-frontend/.env` | Parametriza la URL del backend consumida en tiempo de build/ejecución. |
| Configuración DRF/JWT | `tickethelp-backend/tickethelp/settings.py` | Define `DEFAULT_PERMISSION_CLASSES`, `DEFAULT_AUTHENTICATION_CLASSES` y parámetros de `simplejwt`. |
| Migraciones de datos | `tickethelp-backend/tickets/migrations/0007_create_default_estados.py` | Puebla datos maestros (`Estado`) requeridos por la lógica de negocio. |
| Módulo de vistas de tickets | `tickethelp-backend/tickets/views.py` | Contiene la definición de clases/vistas DRF enrutadas por `tickets/urls.py`. |

## 3. Tabla de no conformidades técnicas de los SCI

| # | SCI afectado | Descripción de la no conformidad | Evidencia (archivo:línea) | Impacto sobre la gestión de la configuración | Severidad |
|---|---|---|---|---|---|
| SCI-01 | `package.json` | Dependencia `next` (framework alternativo, Next.js) declarada sin ningún consumidor en el árbol de código fuente del proyecto, que está construido íntegramente sobre Vite. | `tickethelp-frontend/package.json` (bloque `dependencies`) | Incrementa la superficie de la línea base de configuración con un componente no trazable a ningún requisito; añade peso y superficie de vulnerabilidad (`npm audit`) sin justificación funcional. | Baja |
| SCI-02 | `.env` | El identificador de línea base `VITE_BACKEND_URL` está mal formado (`https:tickethelp-backend.onrender.com`, sin `//`) y, adicionalmente, no corresponde al nombre de variable leído por ningún módulo fuente (`VITE_API_URL`). Existen por tanto **dos identificadores de configuración distintos para el mismo propósito**, uno de los cuales nunca se resuelve. | `.env:1`; `src/api/client.js:1`; `src/api/clienteApi.js:4`; `src/lib/api.js:1` | Rompe la trazabilidad entre el SCI de entorno y el SCI de código: un cambio en `.env` no tiene efecto observable en el sistema desplegado, lo que puede inducir a un operador de despliegue a creer que ha reconfigurado el backend consumido cuando en realidad el valor por defecto (`http://localhost:8000`) permanece activo. | Alta |
| SCI-03 | `tickets/views.py` | El identificador de clase `TicketHistoryAV` no es único dentro de su unidad de compilación (módulo Python): existen dos definiciones completas y funcionalmente distintas bajo el mismo nombre. | `tickets/views.py:563` (definición muerta) y `tickets/views.py:760` (definición activa, enrutada por `tickets/urls.py:39`) | Viola el atributo de identificación única exigible a todo SCI (un nombre de símbolo debe resolver a una única implementación); genera riesgo de que ediciones futuras se apliquen sobre la definición inerte, produciendo una divergencia silenciosa entre lo editado y lo efectivamente desplegado. | Media |
| SCI-04 | `reports/views.py` | Inconsistencia de la línea base de seguridad entre SCI hermanos: de 14 vistas de estadísticas, 10 declaran explícitamente `permission_classes = [IsAdmin]` y 4 omiten el atributo, heredando silenciosamente el permiso global menos restrictivo. | `reports/views.py:671` (`TicketAgingTopView`), `:744` (`WeekdayResolutionCountView`), `:928` (`TTATotalView`), `:997` (`ActiveClientsMonthlyComparisonView`), contrastado con `reports/urls.py:20-64` (comentarios "solo administradores" para las 14 rutas por igual) | La política de seguridad no está gestionada como un atributo de configuración explícito y uniforme sobre el conjunto de SCI del mismo tipo (vistas de reporte), sino que depende de un valor por omisión no declarado localmente; esto impide auditar la política de acceso por simple inspección de cada archivo y facilita regresiones en vistas nuevas que olviden declarar el permiso. | Alta |
| SCI-05 | `src/api/client.js`, `src/api/clienteApi.js`, `src/lib/api.js` | Tres SCI redundantes (clientes HTTP) implementan la misma responsabilidad (adjuntar token JWT, resolver `BASE_URL`, normalizar errores de API) con lógica de extracción de error divergente entre ellos (uno extrae `detail`/`message`/`error` con fallback a claves dinámicas, otro sólo `detail`). | `tickethelp-frontend/src/api/client.js`, `src/api/clienteApi.js`, `src/lib/api.js` | Multiplica por 3 el costo de mantenimiento de un único requisito no funcional (manejo uniforme de errores HTTP) y crea el riesgo de que una corrección de seguridad o de UX (p. ej. GAP-05) se aplique en un solo cliente y no en los otros dos, dejando pantallas con comportamiento inconsistente ante el mismo código de error del backend. | Media |

## 4. No conformidades presumidas en el alcance original y descartadas tras inspección

Para preservar el rigor técnico exigido, se deja constancia de que las siguientes hipótesis de auditoría de configuración **no se confirmaron**:

- **`sendgrid` ausente de `requirements.txt`:** descartado — `sendgrid==6.11.0` está declarado.
- **Migración `0007_create_default_estados.py` no idempotente:** descartado — usa `Estado.objects.get_or_create(...)`, patrón idempotente verificado por inspección directa del código de la migración.

## 5. Recomendaciones de gestión de la configuración

1. Establecer una única fuente de verdad para variables de entorno del frontend (`VITE_API_URL`), documentada en un `.env.example` versionado, y eliminar el identificador huérfano `VITE_BACKEND_URL`.
2. Incorporar una regla de lint/CI (o una prueba de humo, como la incluida en este banco de pruebas) que falle el build si una clase Python se redefine dentro del mismo módulo.
3. Definir la política `permission_classes` como obligatoria y explícita para toda vista nueva bajo `reports/`, reforzada con una prueba de regresión automatizada (ver `SEC-01` en `PLAN_DE_PRUEBAS_Y_RESULTADOS.md`).
4. Consolidar los tres clientes HTTP del frontend en un único módulo, reduciendo el número de SCI redundantes de 3 a 1.
5. Mantener el documento `REQUERIMIENTOS_Y_HC.md` actualizado en `_audit_docs/` como línea base SRS de contraste para futuras auditorías de configuración, dado que en esta ronda permitió confirmar la trazabilidad de NC-SCI-02 contra el requisito RNF-06 y las historias de usuario de control de acceso.
