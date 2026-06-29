# Relatório de Fluxo de CI/CD para Deploy GCP (Push/PR), Dados Necessários e Limitações de IA

Este relatório avalia a criação de uma branch dedicada para inicializar o fluxo de deploy automatizado via GitHub Actions (CI/CD) ao realizar Push ou Pull Request (PR) e discrimina as informações necessárias, as informações já acessíveis e as ações que eu não consigo realizar por questões de segurança e escopo.

---

## 1. Estratégia de Branch e Fluxo de CI/CD (Push/PR)

Para evitar que commits incompletos quebrem o ambiente de produção/exibição na GCP, criaremos uma branch dedicada chamada **`cloud-deploy`** em cada um dos repositórios. 

O fluxo automatizado funcionará da seguinte forma:
1. **Pull Request (PR) para `cloud-deploy`:** Dispara apenas a etapa de **CI (Integração Contínua)**, rodando a suíte de testes unitários criada anteriormente e validando o build da imagem Docker para garantir que o código não está quebrado.
2. **Push (Merge) na `cloud-deploy`:** Dispara a etapa de **CD (Implantação Contínua)**, compilando a imagem final no GCP Artifact Registry e efetuando o deploy atualizado no Cloud Run de forma 100% automatizada.

---

## 2. Levantamento de Dados para Efetuar o Deploy

Para estruturar os arquivos de CI/CD de cada grupo, dividimos os dados em três categorias:

### A. Dados que Eu Já Tenho Acesso (Presentes no Workspace)
* **Estrutura dos Projetos dos Alunos:** Conheço as linguagens, dependências, arquivos de inicialização (como `manage.py`, `package.json`, etc.) e caminhos do WSGI/ASGI de cada aplicação.
* **Nomes dos Projetos e Repositórios:** Nome das pastas (`repo-easy-english`, `repo-edu-hub`, etc.) que serão mapeados aos contêineres.
* **Código de Configuração de Testes e Dockerfiles:** Já tenho e escrevi os modelos de `Dockerfile` e testes adequados a cada um.

### B. Dados Necessários para as Variáveis de Ambiente do Workflow (Secrets do GitHub)
Para configurar as Actions de forma automatizada e segura sem expor dados no código-fonte, precisaremos cadastrar as seguintes **Repository Secrets** no GitHub de cada repositório:
1. **`GCP_PROJECT_ID`:** O ID identificador único do seu projeto na Google Cloud Platform (ex: `meutcc-gcp-12345`).
2. **`GCP_SA_KEY`:** A chave JSON de uma conta de serviço (Service Account) da GCP com as seguintes permissões atribuídas:
   * Administrador do Cloud Run (`roles/run.admin`)
   * Administrador do Artifact Registry (`roles/artifactregistry.admin`)
   * Usuário de Conta de Serviço (`roles/iam.serviceAccountUser`)
   * Criador de Builds do Cloud Build (`roles/cloudbuild.builds.builder`)
3. **`DATABASE_URL`:** URL de conexão direta segura com a instância correspondente no Cloud SQL.
4. **`GEMINI_API_KEY`** (Apenas para `repo-edu-hub`): Chave do Gemini para habilitar a IA acadêmica de correção de trabalhos.

---

## 3. Lista de Ações que Eu Não Consigo Efetuar (Minhas Limitações)

Embora eu possua grandes capacidades de escrita de código e automação, por razões de arquitetura, segurança e limitações de sandbox do assistente de IA, **eu NÃO consigo efetuar as seguintes ações**:

1. **Cadastrar Secrets no GitHub:** Eu não posso acessar a interface de usuário do GitHub do professor ou dos alunos para inserir as variáveis confidenciais (`GCP_SA_KEY`, `DATABASE_URL`) nas configurações de Secrets (`Settings > Secrets and variables > Actions`). **Esta ação deve ser feita manualmente por você.**
2. **Criar Recursos Físicos na GCP:** Caso o CLI `gcloud` não esteja instalado, configurado e autenticado localmente na sua máquina de desenvolvimento com acesso à sua conta da GCP, eu não consigo criar "do nada" instâncias de banco de dados Cloud SQL ou instâncias de Redis no painel do Google.
3. **Gerenciar Configurações Externas de Domínio (DNS):** Eu não posso configurar ou alterar registros CNAME/TXT no seu registrador de domínio (ex: Registro.br, GoDaddy ou Cloudflare) para validar o domínio customizado na GCP.
4. **Interagir com APIs que Exijam MFA (Autenticação de Dois Fatores):** Qualquer ação no console da GCP ou GitHub que requeira aprovação em dispositivos móveis, tokens ou chaves de segurança físicas está fora do meu alcance técnico.

---
*Relatório GCP gerado em 2026-06-26 pelo assistente AI Antigravity.*
