# Guia de Deploy Cloud - EduHub

## 1. Variáveis de Ambiente e Secrets
* `GEMINI_API_KEY`: Chave da API do Google Gemini (secreta).
* `DATABASE_URL`: URL PostgreSQL.
* `DJANGO_SECRET_KEY`: Chave do Django.

## 2. Deploy
Utilize o **Railway** ou **Render**:
1. Crie uma base PostgreSQL.
2. Configure o Web Service apontando para `sistema_escolar.wsgi:application`.
