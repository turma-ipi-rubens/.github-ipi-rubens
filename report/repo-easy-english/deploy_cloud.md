# Guia de Deploy Cloud - Easy English (Render)

Para implantar esta aplicação Django no **Render**:

## 1. Variáveis de Ambiente e Secrets
Cadastre as seguintes variáveis no painel da nuvem:
* `DJANGO_SECRET_KEY`: Chave secreta longa e aleatória.
* `DJANGO_DEBUG`: `False`.
* `DJANGO_ALLOWED_HOSTS`: `<seu-subdominio>.onrender.com`.
* `DATABASE_URL`: URL de conexão do banco PostgreSQL integrado do Render.

## 2. Passos para Deploy
1. Crie um novo **Web Service** no Render apontando para o seu repositório do GitHub.
2. Defina o **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
3. Defina o **Start Command**: `gunicorn easyenglish.wsgi:application`
