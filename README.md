# TicketHelp — Auditoría Técnica, Aseguramiento de Calidad y Estabilización

**Modalidad:** Ejecución unipersonal
**Auditora de Software y QA:** María José López Reyes (Código: 1152268)
**Asignatura:** Gestión y Aseguramiento de la Calidad en Proyectos de Software — UFPS (2026-II)
**Docentes evaluadoras:** Ing. Judith del Pilar Rodríguez Tenjo, Ing. Jessica Lorena Leal Pabón

## Descripción

Este repositorio unifica, en formato monorepo, el sistema TicketHelp (backend Django/DRF + frontend React/Vite) heredado del desarrollo original del equipo, junto con el arnés de pruebas automatizadas y la documentación formal generados durante el ejercicio de auditoría de ingeniería inversa y aseguramiento de la calidad (ISO/IEC 25010 e ISO/IEC/IEEE 29119).

## Estructura del repositorio

```
tickethelp-workspace/
├── tickethelp-backend/     # Django 5 / DRF — código heredado, sin modificar
├── tickethelp-frontend/    # React 19 / Vite — código heredado, sin modificar
├── _qa_test_suite/         # Arnés de pruebas desacoplado (pytest, node:test)
├── docs/                   # Documentación formal de auditoría y requerimientos
└── README.md
```

## Estado del proyecto: Baseline 1.0 vs Baseline 3.0

| | **Baseline 1.0** — código heredado | **Baseline 3.0** — auditoría y certificación de calidad |
|---|---|---|
| Contenido | `tickethelp-backend/`, `tickethelp-frontend/` tal como fueron entregados por el equipo original | Suma de Baseline 1.0 + `_qa_test_suite/` + `docs/` + `README.md` |
| Pruebas automatizadas | No existía un arnés desacoplado ejecutable de forma determinista | 23 pruebas backend (pytest) + 9 pruebas frontend (`node:test`) |
| Resultado de pruebas backend | N/A | 23/23 ejecutadas según diseño (incluye casos que documentan intencionalmente no conformidades reales, ver `docs/GAP_ANALYSIS_INFORME.md`) |
| Resultado de pruebas frontend | N/A | 7/9 aprobadas; 2/9 reproducen de forma determinista la no conformidad de configuración de `.env` |
| Cobertura de línea (tickets/users/reports) | N/A | **36 %** (1319/2046 líneas no cubiertas) |
| Documentación formal | Documentos base de requerimientos e historias de usuario | + Gap Analysis, Plan de Pruebas ISO/IEC/IEEE 29119 y Auditoría de Configuración (SCI) |
| Etiqueta Git | `v1.0-baseline-heredada` | `v3.0-baseline-certificada` |

## Documentación

Ver [`docs/`](docs/) para el conjunto completo de artefactos de auditoría:

- [`docs/GAP_ANALYSIS_INFORME.md`](docs/GAP_ANALYSIS_INFORME.md) — matriz de no conformidades verificadas por inspección real del código.
- [`docs/PLAN_DE_PRUEBAS_Y_RESULTADOS.md`](docs/PLAN_DE_PRUEBAS_Y_RESULTADOS.md) — inventario de casos de prueba (ISO/IEC/IEEE 29119) con precondiciones, aserciones y resultado real de ejecución.
- [`docs/AUDITORIA_CONFIGURACION_INFORME.md`](docs/AUDITORIA_CONFIGURACION_INFORME.md) — no conformidades de los Elementos de Configuración del Software (SCI).
- [`docs/REQUERIMIENTOS_Y_HC.md`](docs/REQUERIMIENTOS_Y_HC.md) — requerimientos e historias de usuario del proyecto.
- [`docs/Ficha Técnica del Software.md`](docs/Ficha%20Técnica%20del%20Software.md) — ficha técnica de referencia.

## Arnés de pruebas

Ver [`_qa_test_suite/`](_qa_test_suite/) — aislado del código fuente auditado, sin dependencias añadidas a `tickethelp-backend/` ni `tickethelp-frontend/`.

### Backend (pytest + cobertura)

Requiere el entorno virtual `_qa_test_suite/venv_qa` ya provisionado (Python 3.11, pytest, pytest-django, pytest-cov).

```powershell
cd _qa_test_suite
.\venv_qa\Scripts\python.exe -m pytest backend_tests/ -v --cov=tickets --cov=users --cov=reports --cov-report=term-missing --cov-report=html:reports/coverage_html
```

### Frontend (node:test, requiere Node.js 22+)

```powershell
cd _qa_test_suite
node --test frontend_tests/test_client_resilience.mjs
```

## Regla de integridad del código heredado

El contenido de `tickethelp-backend/` y `tickethelp-frontend/` se incorporó a este monorepo mediante `git subtree`, preservando íntegramente el historial de commits original de ambos proyectos. Cualquier corrección derivada de los hallazgos de auditoría debe implementarse como un commit explícito y trazable sobre esta línea base, nunca como una reescritura silenciosa del historial heredado.
