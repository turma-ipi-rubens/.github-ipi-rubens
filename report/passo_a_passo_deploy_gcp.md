# Passo a Passo Completo para Deploy das Aplicações na GCP e Lista de Minhas Capacidades

Este guia detalha o procedimento prático e específico para implantar cada um dos TCCs (excluindo o *Skillex*) na Google Cloud Platform (GCP) utilizando o **Google Cloud Run** e o **Cloud SQL**, associados ao seu domínio customizado. Na seção final, listo detalhadamente todas as atividades e alterações de código que eu, como assistente de IA, sou capaz de realizar diretamente no seu ambiente de trabalho para executar este plano.

---

## 1. Pré-Requisitos Globais na GCP (Configuração Única)

Antes de implantar as aplicações individualmente, execute os seguintes passos no console do Google Cloud ou no Cloud Shell para preparar o ambiente:

### A. Criar a Instância PostgreSQL no Cloud SQL
Suba uma única instância do PostgreSQL que servirá a todos os grupos acadêmicos:
```bash
gcloud beta sql instances create tcc-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=southamerica-east1 \
    --root-password="senha_mestra_postgres"
```
*(Utilizamos a máquina `db-f1-micro` por questões de economia e custo controlado para demonstrações acadêmicas).*

Agora, crie os bancos de dados lógicos individuais para cada grupo para isolar o ambiente deles:
```bash
gcloud sql databases create easy_english_db --instance=tcc-postgres
gcloud sql databases create edu_hub_db --instance=tcc-postgres
gcloud sql databases create enlace_db --instance=tcc-postgres
gcloud sql databases create myserver_db --instance=tcc-postgres
gcloud sql databases create rack_plus_db --instance=tcc-postgres
```

### B. Criar a Instância Redis (Apenas para `repo-rack-plus`)
Para suportar as mensagens em tempo real dos WebSockets do Rack Plus:
```bash
gcloud redis instances create rack-redis \
    --size=1 \
    --region=southamerica-east1 \
    --tier=basic
```

---

## 2. Passo a Passo Específico para Deploy de Cada Aplicação

### A. **`repo-easy-english`** (Django + Postgres)
1. **Configuração da Imagem Docker:**
   Acesse a pasta da aplicação e envie o código para ser compilado no Artifact Registry:
   ```bash
   gcloud builds submit --tag southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/easy-english:latest
   ```
2. **Deploy no Cloud Run:**
   Implante a aplicação apontando para a base Postgres do Cloud SQL criada no passo 1:
   ```bash
   gcloud run deploy easy-english \
       --image=southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/easy-english:latest \
       --region=southamerica-east1 \
       --allow-unauthenticated \
       --set-env-vars="DJANGO_SECRET_KEY=sua_chave_secreta,DJANGO_DEBUG=False,DATABASE_URL=postgres://postgres:senha_mestra_postgres@/easy_english_db?host=/cloudsql/[PROJECT_ID]:southamerica-east1:tcc-postgres" \
       --add-cloudsql-instances=[PROJECT_ID]:southamerica-east1:tcc-postgres
   ```
3. **Mapeamento do Domínio:**
   Mapeie `easy-english.seu-dominio.com` para o serviço recém-criado.

---

### B. **`repo-edu-hub`** (Django + Gemini AI)
1. **Compilar a Imagem:**
   ```bash
   gcloud builds submit --tag southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/edu-hub:latest
   ```
2. **Deploy no Cloud Run:**
   Além das credenciais do banco, passe a chave de acesso do Gemini como variável de ambiente para habilitar a IA acadêmica de correção e detecção de plágio:
   ```bash
   gcloud run deploy edu-hub \
       --image=southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/edu-hub:latest \
       --region=southamerica-east1 \
       --allow-unauthenticated \
       --set-env-vars="DJANGO_SECRET_KEY=sua_chave_secreta,DJANGO_DEBUG=False,DATABASE_URL=postgres://postgres:senha_mestra_postgres@/edu_hub_db?host=/cloudsql/[PROJECT_ID]:southamerica-east1:tcc-postgres,GEMINI_API_KEY=[SUA_GEMINI_API_KEY]" \
       --add-cloudsql-instances=[PROJECT_ID]:southamerica-east1:tcc-postgres
   ```
3. **Mapeamento do Domínio:**
   Mapeie `edu-hub.seu-dominio.com` para o serviço.

---

### C. **`repo-enlace`** (Fullstack Node.js + React + Prisma)
O projeto Enlace possui backend e frontend desacoplados. Precisamos de dois serviços separados:

1. **Deploy do Backend (API):**
   * Enviar imagem Docker do backend:
     ```bash
     cd backend
     gcloud builds submit --tag southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/enlace-backend:latest
     ```
   * Deploy no Cloud Run:
     ```bash
     gcloud run deploy enlace-backend \
         --image=southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/enlace-backend:latest \
         --region=southamerica-east1 \
         --allow-unauthenticated \
         --set-env-vars="DATABASE_URL=postgresql://postgres:senha_mestra_postgres@/enlace_db?host=/cloudsql/[PROJECT_ID]:southamerica-east1:tcc-postgres,JWT_SECRET=segredo_jwt" \
         --add-cloudsql-instances=[PROJECT_ID]:southamerica-east1:tcc-postgres
     ```
   * Mapeie `api.enlace.seu-dominio.com` para este serviço do backend.

2. **Deploy do Frontend (React + Nginx):**
   * Compile a imagem passando como parâmetro a URL da API que acabamos de implantar:
     ```bash
     cd ../frontend
     gcloud builds submit --tag southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/enlace-frontend:latest \
         --build-arg="VITE_API_URL=https://api.enlace.seu-dominio.com"
     ```
   * Deploy no Cloud Run (Apenas servindo os arquivos estáticos compilados via Nginx):
     ```bash
     gcloud run deploy enlace-frontend \
         --image=southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/enlace-frontend:latest \
         --region=southamerica-east1 \
         --allow-unauthenticated
     ```
   * Mapeie `enlace.seu-dominio.com` para este serviço do frontend.

---

### D. **`repo-myserver`** (Django REST Framework)
1. **Compilar a Imagem:**
   ```bash
   gcloud builds submit --tag southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/myserver:latest
   ```
2. **Deploy no Cloud Run:**
   ```bash
   gcloud run deploy myserver \
       --image=southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/myserver:latest \
       --region=southamerica-east1 \
       --allow-unauthenticated \
       --set-env-vars="DJANGO_SECRET_KEY=sua_chave,DJANGO_DEBUG=False,DATABASE_URL=postgres://postgres:senha_mestra_postgres@/myserver_db?host=/cloudsql/[PROJECT_ID]:southamerica-east1:tcc-postgres" \
       --add-cloudsql-instances=[PROJECT_ID]:southamerica-east1:tcc-postgres
   ```
3. **Mapeamento do Domínio:**
   Mapeie `myserver.seu-dominio.com` para o serviço.

---

### E. **`repo-rack-plus`** (Django Channels / WebSockets)
Este projeto requer tratamento especial porque o Daphne precisa se conectar ao cache Redis do Memorystore:

1. **Obter o IP da Instância Redis:**
   ```bash
   gcloud redis instances describe rack-redis --region=southamerica-east1 --format="value(host)"
   ```
   *(Considere que o IP retornado seja `10.0.0.3`)*
2. **Compilar a Imagem:**
   ```bash
   gcloud builds submit --tag southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/rack-plus:latest
   ```
3. **Deploy no Cloud Run com Suporte VPC:**
   O Cloud Run precisa se conectar à rede VPC interna do Google para enxergar o Redis Memorystore:
   ```bash
   gcloud run deploy rack-plus \
       --image=southamerica-east1-docker.pkg.dev/[PROJECT_ID]/tcc-apps/rack-plus:latest \
       --region=southamerica-east1 \
       --allow-unauthenticated \
       --vpc-connector=tcc-vpc-connector \
       --set-env-vars="DJANGO_SECRET_KEY=sua_chave,DJANGO_DEBUG=False,DATABASE_URL=postgres://postgres:senha_mestra_postgres@/rack_plus_db?host=/cloudsql/[PROJECT_ID]:southamerica-east1:tcc-postgres,REDIS_URL=redis://10.0.0.3:6379/0" \
       --add-cloudsql-instances=[PROJECT_ID]:southamerica-east1:tcc-postgres
   ```
4. **Mapeamento do Domínio:**
   Mapeie `rack-plus.seu-dominio.com` para o serviço.

---

## 3. O Que Eu Sou Capaz de Fazer para Executar Esse Plano?

Como o assistente de IA **Antigravity**, eu possuo privilégios para executar modificações de arquivos locais e acionar comandos no shell do seu sistema. Veja o que eu posso fazer diretamente agora se você desejar:

### ✅ Alterações de Código-Fonte e Preparação Tecnológica
* **Modificação do `settings.py` dos projetos Django:** Posso alterar os códigos dos alunos para trocar as configurações de banco de dados SQLite estáticas e forçar a leitura do PostgreSQL via `dj_database_url` e injetar suporte seguro a variáveis de ambiente em produção.
* **Criação de Arquivos de Configuração de Produção:** Escrever e atualizar automaticamente `requirements.txt` adicionando pacotes exigidos em produção (`gunicorn`, `daphne`, `dj-database-url`, `psycopg2-binary`).
* **Adaptação de Middlewares do Django:** Inserir e configurar de forma transparente o suporte a servir arquivos estáticos em nuvem via biblioteca `WhiteNoise`.
* **Criação de novos arquivos Dockerfile/docker-compose personalizados:** Escrever arquivos `Dockerfile`, arquivos de configuração de servidores `nginx.conf` e scripts de automação.

### ✅ Automação de CI/CD (GitHub Actions)
* **Criação de Workflows Automatizados:** Escrever arquivos YAML sob a pasta `.github/workflows/` de cada projeto para fazer o build automático no Artifact Registry e o deploy contínuo no Cloud Run da GCP a cada `git push` executado pelos alunos.

### ⚠️ Execução de Comandos GCP (Restrição de Shell local)
* **Executar comandos locais do gcloud SDK:** Posso disparar a compilação local de containers e comandos de deploy (`gcloud run deploy`, `gcloud builds submit`, `gcloud sql databases create`) diretamente do terminal powershell do seu sistema de desenvolvimento **caso você tenha o SDK do gcloud instalado, autenticado e com as permissões corretas configuradas na sua máquina.**

---
*Relatório GCP gerado em 2026-06-26 pelo assistente AI Antigravity.*
