# Relatório de Dockerização e Orquestração dos Projetos

Este relatório apresenta as alterações necessárias nos códigos dos projetos para suportar a conteinerização com Docker, além de fornecer os arquivos `Dockerfile` e `docker-compose.yml` recomendados para cada tipo de arquitetura identificada nos repositórios.

---

## 1. Alterações Necessárias no Código-Fonte

Para que as aplicações rodem corretamente dentro de contêineres e sejam portáveis, é fundamental ajustar o código-fonte seguindo os princípios de *12-Factor App*:

### A. Parametrização por Variáveis de Ambiente
* **Django (`settings.py`):**
  * **Chave Secreta (`SECRET_KEY`):** Não deve ficar exposta no código. Deve ser lida do ambiente:
    ```python
    import os
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-insecure-key')
    DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
    ```
  * **Banco de Dados (`DATABASES`):** Em vez de apontar para o SQLite local, configure para ler as credenciais do ambiente (para integração com PostgreSQL no compose):
    ```python
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
        )
    }
    ```
    *(Nota: Requer a instalação do pacote `dj-database-url` e `psycopg2-binary` no `requirements.txt`).*

* **Node.js / Express (`backend`):**
  * Garantir que o servidor Express escute no host `0.0.0.0` em vez de `localhost` ou `127.0.0.1`, caso contrário, as requisições vindas de fora do contêiner serão recusadas:
    ```javascript
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`Servidor rodando na porta ${PORT}`);
    });
    ```
  * O arquivo `schema.prisma` deve ler a URL de conexão do banco de dados através da variável `DATABASE_URL`:
    ```prisma
    datasource db {
      provider = "postgresql"
      url      = env("DATABASE_URL")
    }
    ```

### B. Dependências e Servidores de Produção
* **Django:** Adicionar `gunicorn` (para aplicações WSGI normais como Easy English, EduHub, MyServer, NexusNode) ou `daphne`/`uvicorn` (para Rack Plus, que utiliza Django Channels/WebSockets) no `requirements.txt`.
* **Vite / React:** Em produção, a SPA deve ser compilada com `npm run build` e servida por um servidor web leve como o **Nginx**, em vez do servidor de desenvolvimento do Vite.

---

## 2. Dockerfiles por Tipo de Aplicação

### A. Python / Django (Para `repo-easy-english`, `repo-edu-hub`, `repo-myserver`, `repo-nexusnode`)

Crie o arquivo `Dockerfile` na raiz do respectivo projeto:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Evita que o Python escreva arquivos .pyc e bufferize a saída do log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias para pacotes como psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do projeto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn dj-database-url psycopg2-binary

# Copia o código fonte
COPY . /app/

# Expõe a porta padrão do Django
EXPOSE 8000

# Executa migrações e inicia o servidor de produção
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 --workers 3 configuracao.wsgi:application"]
```
*(Substitua `configuracao.wsgi:application` pelo caminho correto do arquivo wsgi de cada projeto, por exemplo `bdjango.wsgi:application` para MyServer ou `sistema_escolar.wsgi:application` para EduHub).*

---

### B. Django com WebSockets/Channels (Para `repo-rack-plus`)

Como o `repo-rack-plus` utiliza Django Channels (WebSockets), precisamos usar o `daphne` como servidor ASGI:

```dockerfile
# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir daphne dj-database-url psycopg2-binary

COPY . /app/

EXPOSE 8000

# O Daphne gerencia conexões HTTP normais e WebSockets na porta 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]
```

---

### C. Node.js Backend com Prisma (Para `repo-enlace/backend`)

Crie em `repo-enlace/backend/Dockerfile`:

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /usr/src/app

COPY package*.json ./
COPY prisma ./prisma/

# Instala dependências e gera o cliente Prisma
RUN npm ci
RUN npx prisma generate

COPY . .

EXPOSE 3000

# Roda as migrações do banco e inicia a API
CMD ["sh", "-c", "npx prisma migrate deploy && npm start"]
```

---

### D. React com Vite e Nginx (Para `repo-enlace/frontend`)

Crie em `repo-enlace/frontend/Dockerfile`:

```dockerfile
# Estágio de Build
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Variável de ambiente consumida na compilação do Vite
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Estágio de Produção (Servidor Nginx)
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Copia configuração customizada do Nginx para suportar roteamento SPA (React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

*Nota: Crie também o arquivo `repo-enlace/frontend/nginx.conf`:*
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 3. Orquestração com Docker Compose

### A. Para Projetos Web Django + PostgreSQL (`repo-easy-english`, `repo-edu-hub`, `repo-myserver`)

Abaixo está o modelo `docker-compose.yml` para rodar a aplicação web Django integrada a um banco de dados PostgreSQL persistente:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: django_db
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=app_db
      - POSTGRES_USER=app_user
      - POSTGRES_PASSWORD=app_password
    ports:
      - "5432:5432"

  web:
    build: .
    container_name: django_app
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=sua_chave_secreta_super_segura
      - DJANGO_DEBUG=False
      - DJANGO_ALLOWED_HOSTS=*
      - DATABASE_URL=postgres://app_user:app_password@db:5432/app_db
    depends_on:
      - db

volumes:
  postgres_data:
```

---

### B. Para `repo-rack-plus` (Django + WebSockets + Redis + PostgreSQL)

Para suportar o Django Channels, adicionamos um serviço **Redis** como camada de canais (*Channel Layer*):

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: rack_plus_db
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=rack_db
      - POSTGRES_USER=rack_user
      - POSTGRES_PASSWORD=rack_password

  redis:
    image: redis:7-alpine
    container_name: rack_plus_redis
    restart: always

  web:
    build: .
    container_name: rack_plus_web
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=chave_de_producao_secreta
      - DJANGO_DEBUG=False
      - DATABASE_URL=postgres://rack_user:rack_password@db:5432/rack_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

### C. Para `repo-enlace` (Frontend React + Backend Node.js/Prisma + PostgreSQL)

Orquestração completa contendo a API do Backend, o Banco de dados PostgreSQL e o Frontend servido por Nginx:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: enlace_db
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=enlace_db
      - POSTGRES_USER=enlace_user
      - POSTGRES_PASSWORD=enlace_password
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    container_name: enlace_backend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://enlace_user:enlace_password@db:5432/enlace_db?schema=public
      - JWT_SECRET=segredo_do_token_jwt
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_URL=http://localhost:3000
    container_name: enlace_frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---
*Relatório gerado automaticamente em 2026-06-23 pelo assistente AI Antigravity.*
