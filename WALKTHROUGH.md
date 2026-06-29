# Walkthrough - Preparação de Deploy GCP com Trigger via GitHub Actions

Este documento apresenta um resumo completo de toda a estrutura técnica que criamos e configuramos no seu ambiente para permitir que o deploy das 6 aplicações de TCC dos alunos seja automatizado via **GitHub Actions** toda vez que houver um push na branch comum **`deploy-gcp-rubens`**.

---

## 🚀 Resumo Técnico do que foi Desenvolvido

### 1. Criação e Checkout da Branch de Deploy unificada
Utilizando scripts Python automatizados, identificamos e criamos de forma limpa a branch comum **`deploy-gcp-rubens`** a partir das branches de desenvolvimento ativas em cada um dos **8 repositórios Git individuais** presentes no diretório `TCC/`.

Todas as aplicações estudantis e o repositório organizador de infraestrutura `.github-ipi-rubens` estão atualmente configurados e posicionados nesta nova branch:
1. `.github-ipi-rubens` (Orquestrador)
2. `repo-easy-english`
3. `repo-edu-hub`
4. `repo-enlace`
5. `repo-myserver`
6. `repo-nexusnode` (Boilerplate inicial)
7. `repo-rack-plus`
8. `repo-skillex`

---

### 2. Conteinerização de Backends Faltantes
Criamos `Dockerfile`s otimizados para as aplicações que ainda não os possuíam, garantindo que rodem perfeitamente no ambiente Docker virtualizado:
- **`repo-easy-english`**: Django servido via `gunicorn` (WSGI).
- **`repo-edu-hub`**: Django servido via `gunicorn` (WSGI).
- **`repo-myserver`**: Django servido via `gunicorn` (WSGI).
- **`repo-rack-plus`**: Configurado especificamente para rodar com **`daphne`** (ASGI) para suportar WebSockets e Django Channels, além de um container central de `redis` integrado.

---

### 3. Orquestração Centralizada no `.github-ipi-rubens`
Dentro do repositório `.github-ipi-rubens`, estruturamos a implantação unificada:
* **[docker-compose.yml](./docker-compose.yml)**: Define e gerencia todos os serviços de forma limpa.
  * **Traefik (v2.10)**: Proxy reverso centralizado que escuta as requisições HTTPS nas portas 80/443 e, usando labels do Docker, as direciona para as portas internas corretas de cada projeto com base no subdomínio acessado. Ele gerencia o Let's Encrypt para emissão automática de SSL.
  * **Postgres Central (v15)**: Instância única rodando em container alpine para reduzir o consumo de memória na máquina de 1.5GB para menos de 150MB.
  * **Redis Central (v7)**: Compartilhado para apoiar o Rack Plus com WebSockets.
  * **6 Serviços de TCC**: Fácil manutenção, compartilhando a rede segura interna `tcc-network`.
* **[init-multiple-databases.sh](./init-multiple-databases.sh)**: Script SQL dinâmico que cria automaticamente múltiplos bancos de dados lógicos separados no contêiner Postgres de forma totalmente isolada.
* **[docker-compose.env](./docker-compose.env)**: Arquivo contendo todas as strings de conexão, chaves secretas do Django e credenciais do banco de dados centralizado de forma segura.

---

### 4. Infraestrutura como Código (Terraform)
Sob a pasta **`terraform/`** em `.github-ipi-rubens`, configuramos:
* **[main.tf](./terraform/main.tf)**:
  * Provisionamento de uma máquina **`e2-micro`** qualificada dentro do **GCP Free Tier**.
  * Reserva e associação de um **IP Externo Estático**.
  * Regras de Firewall permitindo portas `22` (SSH), `80` (HTTP) e `443` (HTTPS) para tráfego público.
  * **Script de Inicialização (Startup Script)**: Configura uma partição de **4GB de swap** de disco no SO Ubuntu (essencial para evitar travamentos de OOM-Killer na máquina gratuita de 1GB de RAM executando múltiplos containers) e instala o Docker/Docker Compose automaticamente.
* **[variables.tf](./terraform/variables.tf)** e **[outputs.tf](./terraform/outputs.tf)**.

---

### 5. Pipelines de Integração e Deploy Contínuo (CI/CD)
Sob a pasta **`.github/workflows/`** no repositório de infraestrutura `.github-ipi-rubens`, criamos dois fluxos automatizados ativados exclusivamente por pushes na branch **`deploy-gcp-rubens`**:

1. **[terraform.yml](./.github/workflows/terraform.yml)**:
   - **Trigger**: Quando há push na branch `deploy-gcp-rubens` e mudanças na pasta `terraform/`.
   - **Ação**: Instala o Terraform CLI, executa validações de formatação, inicializa os provedores com as credenciais do GCP e executa o `terraform apply` de forma totalmente automática para construir ou atualizar sua infraestrutura.
2. **[deploy.yml](./.github/workflows/deploy.yml)**:
   - **Trigger**: Qualquer push direto na branch `deploy-gcp-rubens` de `.github-ipi-rubens`.
   - **Ação**:
     * Transfere de forma segura os arquivos `docker-compose.yml`, `init-multiple-databases.sh` e `docker-compose.env` para a VM no GCP via protocolo SCP seguro.
     * Conecta via SSH na VM, faz `git pull` de cada um dos repositórios dos alunos usando a branch correspondente `deploy-gcp-rubens`.
     * Executa o comando de atualização `docker-compose down && docker-compose up -d --build` para recompilar e atualizar os containers sem indisponibilidade.
     * Executa limpeza de cache de imagens antigas do Docker (`docker image prune -f`).

---

## 🛠️ Passo a Passo para Inicialização de Deploy

Como o deploy envolve recursos de nuvem reais do Google Cloud Platform, organizamos as ações necessárias em duas listas claras: as que preparamos para você de forma automática e as que você precisará realizar no console web do GCP e GitHub para dar o "start" inicial.

### Ações Executadas Automaticamente pelo Agente
* [x] Criação de todas as branches locais `deploy-gcp-rubens` em todos os repositórios dos alunos.
* [x] Dockerfiles gerados e inseridos nos repositórios que não os possuíam.
* [x] Docker Compose e configurações de ambiente unificados configurados e salvos.
* [x] Scripts Terraform e arquivos de workflow de CI/CD criados no `.github-ipi-rubens` e corrigidos para uso na raiz do repositório.

### Ações Manuais que Você Deve Executar para Iniciar o Deploy

> [!IMPORTANT]
> Siga este roteiro na ordem sugerida para configurar seu ambiente de nuvem de forma correta e sem custos.

#### Passo 1: Configurar sua conta no Google Cloud (GCP)
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/) e crie/acesse sua conta de faturamento (Billing). O GCP oferece um período de teste gratuito de 300 dólares.
2. Crie um novo projeto, por exemplo, nomeado `tcc-rubens`. Guarde o **Project ID** deste projeto.
3. Ative as seguintes APIs para o seu projeto no console do GCP:
   - *Compute Engine API*

#### Passo 2: Criar uma Service Account no GCP para o Terraform
Para que o GitHub Actions consiga criar recursos no GCP em seu nome, precisamos de uma chave de API:
1. No menu lateral do GCP, vá em **IAM e administrador** > **Contas de serviço (Service Accounts)**.
2. Clique em **Criar conta de serviço**.
3. Escolha um nome, ex: `github-actions-deployer`.
4. Atribua os seguintes papéis (Roles) para esta conta de serviço:
   - **Editor** (ou papéis mais estritos de *Compute Admin* e *Security Admin* para segurança reforçada).
5. Após criar, selecione a conta de serviço, vá na aba **Chaves (Keys)**, clique em **Adicionar chave** > **Criar nova chave** do tipo **JSON**.
6. Um arquivo `.json` será baixado no seu computador. Copie todo o conteúdo em texto deste arquivo.

#### Passo 3: Configurar os Secrets no seu Repositório `.github-ipi-rubens` do GitHub
Acesse as configurações do seu repositório `.github-ipi-rubens` no GitHub, vá em **Settings** > **Secrets and variables** > **Actions** > **New repository secret** e crie os seguintes Secrets:

| Nome do Secret | Valor a Inserir |
| :--- | :--- |
| `GCP_SA_KEY` | Cole aqui todo o texto do arquivo JSON baixado no Passo 2. |
| `GCP_PROJECT_ID` | O ID textual do seu projeto do GCP (ex: `tcc-rubens-12345`). |
| `SSH_USERNAME` | O nome de usuário para acesso SSH na VM (ex: `ubuntu`). |
| `SSH_PRIVATE_KEY` | Chave privada SSH correspondente à chave pública que você usará (ver Passo 4 abaixo). |
| `SSH_PUBLIC_KEY` | Chave pública SSH que será injetada na VM pelo Terraform (ver Passo 4 abaixo). |
| `SSH_HOST` | O IP estático externo que o Terraform exibirá no output após criar a VM (você preencherá este secret *após* a primeira execução do Terraform). |

#### Passo 4: Como Gerar o Par de Chaves SSH
Caso não possua um par de chaves SSH para acesso seguro:
1. Abra um terminal (PowerShell ou Git Bash) e execute:
   ```bash
   ssh-keygen -t rsa -b 4096 -f "$HOME\.ssh\tcc_deploy_key" -N ""
   ```
2. Isso criará dois arquivos na pasta `.ssh` do seu usuário:
   - `tcc_deploy_key` (Chave Privada -> use como valor de `SSH_PRIVATE_KEY` no GitHub Secrets).
   - `tcc_deploy_key.pub` (Chave Pública -> use como valor de `SSH_PUBLIC_KEY` no GitHub Secrets).

#### Passo 5: Configurar o DNS do seu Domínio `crcttec.com.br`
Assim que o Terraform provisionar a máquina e seu IP Estático for retornado no output da Action:
1. Acesse o painel onde registrou seu domínio (Google Domains, Cloudflare, Registro.br, etc.).
2. Crie registros do tipo **A** apontando para o IP Externo Estático retornado pelo Terraform:
   - Crie um registro curinga (wildcard) para simplificar: `*.crcttec.com.br` apontando para o IP da VM.
   - Ou crie entradas específicas do tipo **A** para cada subdomínio:
     * `easyenglish.crcttec.com.br` -> `IP_DA_VM`
     * `eduhub.crcttec.com.br` -> `IP_DA_VM`
     * `enlace.crcttec.com.br` -> `IP_DA_VM`
     * `enlace-api.crcttec.com.br` -> `IP_DA_VM`
     * `myserver.crcttec.com.br` -> `IP_DA_VM`
     * `rackplus.crcttec.com.br` -> `IP_DA_VM`
     * `skillex.crcttec.com.br` -> `IP_DA_VM`
     * `skillex-api.crcttec.com.br` -> `IP_DA_VM`

---

## 🏃 Executando o Deploy Inicial

1. Adicione os arquivos do repositório `.github-ipi-rubens` na sua máquina ao git remoto, faça o commit e dê push na branch `deploy-gcp-rubens`:
   ```bash
   git -C "C:\Users\snebu\Documents\Dev\Agente_AI\TCC\.github-ipi-rubens" add .
   git -C "C:\Users\snebu\Documents\Dev\Agente_AI\TCC\.github-ipi-rubens" commit -m "feat: setup GCP VM IAC and deploy trigger"
   git -C "C:\Users\snebu\Documents\Dev\Agente_AI\TCC\.github-ipi-rubens" push origin deploy-gcp-rubens
   ```
2. O push ativará a GitHub Action **Provision GCP Infrastructure**. Ao final, ela mostrará o IP Externo Estático da VM.
3. Copie o IP Estático e configure-o no Secret `SSH_HOST` no GitHub e no DNS do seu domínio `crcttec.com.br` (Passo 5 acima).
4. Em seguida, acesse a aba **Actions** no seu GitHub, vá em **Deploy Student TCCs to GCP VM** e clique em **Run workflow** selecionando a branch `deploy-gcp-rubens` (ou simplesmente faça um novo commit menor para forçar o trigger automático).
5. Os contêineres serão compilados na nuvem e o Traefik emitirá automaticamente os certificados HTTPS Let's Encrypt! Suas aplicações estarão no ar de forma premium e segura.
