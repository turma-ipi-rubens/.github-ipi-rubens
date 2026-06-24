# Guia de Deploy Cloud - MyServer

## 1. Variáveis
* `DATABASE_URL` (PostgreSQL)
* `DJANGO_SECRET_KEY`

## 2. Deploy
1. Crie um Web Service no Render ou Railway.
2. Start command: `gunicorn bdjango.wsgi:application --bind 0.0.0.0:8000`
