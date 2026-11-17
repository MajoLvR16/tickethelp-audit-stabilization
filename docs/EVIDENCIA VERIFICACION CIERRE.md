# Evidencia de verificación de cierre

**Fecha:** 2026-11-17
**Commit verificado (referencia):** `7ace764` (rama `qa-audit-stabilization`). La segunda auditoría verificó `c657e1e`; los 4 commits posteriores (#9 y #10) solo modifican documentación y un comentario de prueba, sin cambios en el código de la aplicación.
**Verificación posterior a la limpieza:** `6380331` (rama `chore/cierre-final`), con resultados idénticos.
**Entorno del arnés:** Python 3.11, Django 5.2.17 (el repositorio declara 5.0.6 en `requirements.txt`; se anota sin modificar), Node.js 22.14.0.

## 1. Verificación

| Verificación | Referencia | Resultado sobre `7ace764` | Resultado sobre `6380331` | Fuente / comando |
|---|---|---|---|---|
| Pruebas backend | 26/26 | 26/26 | 26/26 | `pytest backend_tests/` |
| Pruebas frontend | 9/9 | 9/9 | 9/9 | `node --test frontend_tests/test_client_resilience.mjs` |
| Cobertura total | 34 % (913/2698) | 34 % (2698 sentencias, 1785 sin cubrir) | 34 % (igual) | `pytest --cov=tickets --cov=users --cov=reports` |
| Cobertura `reports/views.py` | 18 % | 18 % (488 sentencias, 400 sin cubrir) | 18 % | ídem |
| Bundle JS | 985,19 kB | 985,19 kB (2284 módulos) | 985,19 kB (2284 módulos) | `npm run build` |
| Vistas con `IsAdmin` | 13 de 14 | 13 de 14 | 13 de 14 | `tickethelp-backend/reports/views.py` |
| `TechnicianPerformanceView` | `IsAuthenticated` con validación de rol | línea 1077 y validación en la 1087 | igual | `reports/views.py` |
| `TicketHistoryAV` | una sola (~línea 709) | una sola, línea 709 | igual | `tickethelp-backend/tickets/views.py` |
| `next` y `axios` | ausentes | ausentes | ausentes | `package.json`, `package-lock.json` |
| Cliente HTTP único | `src/api/client.js` | único; sin `fetch(` ni `axios` en otros archivos; no existen `src/api/clienteApi.js` ni `src/lib/api.js` | igual | `git grep`, listado de `src/api` y `src/lib` |
| Variable de entorno | `VITE_API_URL` | `.env` y `client.js:1`; 0 usos de `VITE_BACKEND_URL` | igual | `git grep` |
| Protección de `master` | protegida, `6afa257` | protegida; PR obligatorio; `enforce_admins` activo; sin force-push ni borrado; en `6afa257` | no aplica | `gh api repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection` |

No se encontraron diferencias contra las referencias de la segunda auditoría.

## 2. Hallazgos nuevos

- Se encontró documentación de despliegue de terceros (infraestructura ajena al proyecto auditado) en el backend, en dos documentos de `docs/` y en `.env.example`. Se retiró o sustituyó (sección 3).
- El entorno virtual `venv_windows` (5578 archivos) estaba versionado pese a figurar en `.gitignore`.
- Una cita de `AUDITORIA_CONFIGURACION_INFORME.md` apuntaba a una ruta que no existe en el repositorio.
- Django 5.2.17 en el arnés frente a 5.0.6 declarado (observación, sin corrección).

## 3. Limpieza realizada (rama `chore/cierre-final`)

| Commit | Cambio |
|---|---|
| `a3bc2f0` | `README_DEPLOY.md` reemplazado por una referencia al Manual de Despliegue y datos verificables (Dockerfile, variables de `settings.py`, `VITE_API_URL`). No declara un despliegue realizado. |
| `b0e2ae1` | `.env.example` con valores locales de ejemplo. |
| `a7aca56` | Retirados 3 documentos de `docs/` (dos lineamientos y una auditoría previa) ajenos al alcance. |
| `487b017` | Cita de `AUDITORIA_CONFIGURACION_INFORME.md` reescrita sin ruta obsoleta. |
| `6380331` | `venv_windows` deja de versionarse (`git rm -r --cached`; no se borra del disco). |

Barrido sobre el árbol tras la limpieza: sin coincidencias de direcciones IP, dominios de servicios de despliegue de terceros ni términos de herramientas de IA.

**Autoría heredada (se conserva sin cambios):** los README de backend y frontend, un enlace en un componente del frontend, `REQUERIMIENTOS_Y_HC.md` y la Ficha Técnica del Software contienen nombres, usuarios de GitHub y tablas de integrantes del equipo original. Corresponden a la autoría del código y los documentos heredados y se conservan deliberadamente.

**Historial de Git:** no se reescribe. Conserva los autores y mensajes originales del equipo heredado; el barrido de términos de IA y de servicios de despliegue de terceros en los mensajes de commit dio 0 coincidencias de IA y 1 línea de mensaje de despliegue.

## 4. Tags

| Tag | Commit | Estado |
|---|---|---|
| `v1.0-baseline-heredada` | `a52fb54` | existente |
| `v3.0-baseline-certificada` | `255d65a` | existente |
| `v4.0-baseline-remediada` | `7ace764` | creado en esta entrega (anotado) |
| Baseline 2.0 | sin commit identificable en el historial | no creado |

## 5. Pendientes y fuera de alcance

- **Despliegue en Render:** pendiente, fuera de alcance de esta verificación.
- **Solicitudes de cambio opcionales** (no implementadas): CR-09 (validar `VITE_API_URL` con `/^https?:\/\//`), CR-10 (normalizar el manejo de errores que solo usa `console.error`, GAP-05) y CR-11 (pruebas sobre `reports/`, hoy en 18 %).
- **`master`:** sigue en `6afa257` y no contiene CR-01 a CR-08; el merge de `qa-audit-stabilization` a `master` queda como decisión posterior.
