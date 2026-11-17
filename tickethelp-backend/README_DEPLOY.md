# Despliegue del backend

El procedimiento de despliegue está documentado en el **Manual de Despliegue** (documento Word, aparte de este repositorio). Este archivo solo resume lo verificable en el código.

## Imagen Docker (`Dockerfile`)

- Base: `python:3.12-slim`.
- Instala `requirements.txt` y expone el puerto 8000.
- Comando de arranque: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn tickethelp.wsgi:application --bind 0.0.0.0:8000`.

## Variables de entorno leídas en `tickethelp/settings.py`

| Grupo | Variables |
|---|---|
| Núcleo | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` |
| Base de datos | `DATABASE_URL` |
| Almacenamiento S3 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL` |
| Correo | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `EMAIL_TIMEOUT` |
| Notificaciones | `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `NOTIFICATIONS_EMAIL_ENABLED` |

`.env.example` contiene una plantilla mínima.

## Frontend

El frontend lee la URL del backend en `VITE_API_URL` (`tickethelp-frontend/src/api/client.js`). Debe incluir el esquema completo, por ejemplo `https://api.midominio.com`.
