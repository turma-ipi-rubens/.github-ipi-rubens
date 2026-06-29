# Relatório de Viabilidade de Deploy Cloud - TCCs

Com as informações mais atualizadas obtidas diretamente dos repositórios dos alunos (inclusive novos desenvolvimentos como o algoritmo de detecção de plágio no `repo-edu-hub` e as atualizações de telemetria baseadas em banco de dados no `repo-rack-plus`), avaliamos se seria possível efetuar o deploy destas aplicações em ambientes Cloud de forma produtiva ou para fins de demonstração acadêmica.

---

## 1. Status de Viabilidade por Repositório

### A. **`repo-easy-english`** (Branch: `main`)
* **Viabilidade de Deploy:** **Alta**
* **Análise:**
  * O projeto está maduro, bem estruturado, possui modelos bem estabelecidos de controle de flashcards e gravação de sessões de estudo.
  * O deploy cloud da aplicação web Django é extremamente simples (usando PostgreSQL em um PaaS como Render ou Railway).
  * **Obstáculo/Observação:** A extensão do Chrome fornecida no projeto precisa ser instalada localmente no navegador do usuário em modo desenvolvedor (carregada descompactada), mas ela se comunicará perfeitamente com a URL cloud da API Django após o deploy.

### B. **`repo-edu-hub`** (Branch: `EDUHUB-Beta`)
* **Viabilidade de Deploy:** **Alta**
* **Análise:**
  * A branch `EDUHUB-Beta` trouxe implementações recentes e completas para **detecção de plágio acadêmico** utilizando análise de similaridade (`aluno/services/plagio.py`) além da integração de correção automatizada com o Google Gemini.
  * O modelo de banco de dados (`accounts.User`) e tabelas de relacionamento estão consistentes.
  * **Requisito Cloud:** Para que funcione perfeitamente na nuvem, deve-se obrigatoriamente fornecer a secret `GEMINI_API_KEY` para que o serviço do Gemini classifique os trabalhos acadêmicos dos alunos em tempo de execução.

### C. **`repo-enlace`** (Branch: `dev`)
* **Viabilidade de Deploy:** **Alta**
* **Análise:**
  * A branch `dev` consolida o backend em Node.js com persistência via Prisma ORM e o frontend em React/Vite.
  * O deploy full-stack em ambiente cloud (ex: renderizando o frontend como site estático e hospedando o backend como web service) é totalmente viável.
  * **Requisito Cloud:** É essencial configurar uma instância PostgreSQL gerenciada na nuvem e expor a variável de ambiente `DATABASE_URL` para o Prisma rodar os comandos de migração (`npx prisma migrate deploy`) no estágio de build/start.

### D. **`repo-myserver`** (Branch: `US02--Autenticacao-e-Permissões`)
* **Viabilidade de Deploy:** **Média-Alta**
* **Análise:**
  * A aplicação possui uma estrutura robusta de endpoints com Django REST Framework para gerenciamento de servidores de jogos.
  * **Obstáculo de Produção:** Atualmente utiliza uma tabela de autenticação de usuários e hashes de senhas personalizada (`Usuario` em `app/models.py`), o que diminui a segurança nativa.
  * **Viabilidade:** Apesar disso, para fins demonstrativos e acadêmicos, a aplicação é 100% deployável em qualquer nuvem PaaS conectada a um banco PostgreSQL.

### E. **`repo-nexusnode`** (Branch: `main`)
* **Viabilidade de Deploy:** **Baixa** (Apenas esqueleto)
* **Análise:**
  * Sendo apenas a estrutura inicial gerada pelo Django com Django REST Framework instalado (esqueleto vazio sem lógica ou modelos de negócios), o deploy é viável tecnicamente, mas sem finalidade prática uma vez que não existem endpoints ativos.

### F. **`repo-rack-plus`** (Branch: `main`)
* **Viabilidade de Deploy:** **Média-Alta**
* **Análise:**
  * Com as atualizações mais recentes na branch `main`, o projeto evoluiu significativamente, estruturando modelos para gerenciamento de Racks, Salas, Dispositivos e Coletas de Telemetria (`devicetelemetry`, `telemetrylog`).
  * A infraestrutura utiliza Django Channels (WebSockets).
  * **Obstáculo/Requisito de Deploy Cloud:** Diferente de aplicações WSGI simples, o deploy do painel web do Rack Plus exige um servidor ASGI (como **Daphne** ou **Uvicorn**) e uma instância **Redis** rodando na nuvem para servir como `Channel Layer` para os WebSockets de telemetria em tempo real.
  * **O Agente Local:** O executável do agente (`agente/collector.py`) continuará rodando localmente nas máquinas monitoradas dos usuários, enviando os dados JSON de hardware via HTTPS diretamente para a URL do servidor cloud.

### G. **`repo-skillex`** (Branch: `feature/US12`)
* **Viabilidade de Deploy:** **Alta**
* **Análise:**
  * O projeto de troca de serviços e habilidades é o mais maduro arquiteturalmente. Possui arquivos de configuração para produção, suporte nativo a Docker/Docker-compose, suíte de testes end-to-end com Playwright, frontend React PWA e backend robusto Express com Socket.io.
  * Viabilidade total para deploy em instâncias ECS, Kubernetes ou PaaS como Railway utilizando os scripts pré-existentes.

---

## 2. Recomendações Gerais para o Sucesso dos Deploys na Nuvem

Para garantir que todos os deploys funcionem perfeitamente nas plataformas cloud, os alunos devem seguir estes 4 passos cruciais:

1. **Trocar SQLite por PostgreSQL:** O SQLite perde os dados a cada restart do contêiner em nuvens como Render e Heroku. O uso de uma instância gerenciada de PostgreSQL é obrigatório.
2. **Uso do Gunicorn/Daphne:** Nunca utilizar `python manage.py runserver` em produção.
3. **Coleta de Arquivos Estáticos (`collectstatic`):** No Django, deve-se rodar `python manage.py collectstatic --noinput` no comando de build e configurar bibliotecas como `WhiteNoise` para servir os arquivos CSS/JS no ambiente cloud.
4. **Configuração de CORS:** Para projetos desacoplados (como o frontend e backend de `repo-enlace`), certificar-se de liberar o CORS no backend para aceitar requisições originárias do subdomínio cloud onde o frontend React está hospedado.

---
*Relatório de viabilidade gerado em 2026-06-26 pelo assistente AI Antigravity.*
