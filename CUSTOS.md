# Estimativa de Custos de Implantação (Apenas Demonstração)

Este relatório apresenta a estimativa de custos para implantar os 6 TCCs ativos dos alunos para fins de **demonstração acadêmica e avaliação**, priorizando opções gratuitas, de baixo custo e com menor complexidade de infraestrutura.

---

## 1. Visão Geral das Aplicações a Implantar
Para estimar os custos, consideramos as seguintes características de cada repositório:

| Repositório | Stack Principal | Banco de Dados | Dependências Especiais |
| :--- | :--- | :--- | :--- |
| **`repo-easy-english`** | Django (Python) | PostgreSQL | Nenhum |
| **`repo-edu-hub`** | Django (Python) | PostgreSQL | `GEMINI_API_KEY` (Gemini API) |
| **`repo-enlace`** | Node.js + React/Vite | PostgreSQL | Frontend desacoplado do Backend |
| **`repo-myserver`** | Django REST | PostgreSQL | Nenhum |
| **`repo-rack-plus`** | Django Channels (ASGI) | PostgreSQL | Redis (para WebSockets / Telemetria) |
| **`repo-skillex`** | Node.js + React PWA | MongoDB / PostgreSQL | WebSockets (Socket.io) |

*Nota: O `repo-nexusnode` não foi incluído por ser apenas uma estrutura inicial (esqueleto vazio) sem lógica funcional.*

---

## 2. Abordagem de Arquitetura Recomendada (A Mais Barata)

Para demonstração acadêmica de múltiplos microsserviços/projetos leves, hospedar cada aplicação em serviços individuais na nuvem (PaaS) torna-se caro e complexo. Em vez disso, a melhor prática é a **Consolidação em um Servidor Único** ou **Serverless Otimizado**.

Apresentamos as 3 melhores alternativas de baixo custo abaixo:

---

### Alternativa A: Servidor VPS Único com Docker Compose (RECOMENDADO)
Hospedar todas as 6 aplicações rodando como contêineres Docker em uma única Máquina Virtual (VPS), gerenciadas por um proxy reverso automático (como **Traefik** ou **Nginx Proxy Manager**) que gera certificados SSL (HTTPS) gratuitos para cada subdomínio (ex: `easyenglish.seudominio.com`, `eduhub.seudominio.com`).

* **Onde hospedar**:
  * **DigitalOcean / Hetzner / AWS Lightsail**: Um servidor básico de 2 vCPUs e 4GB de RAM é mais do que suficiente para aguentar todas as aplicações simultaneamente para demonstração de baixo tráfego.
  * **GCP (Google Cloud Platform - Free Tier)**: A GCP oferece uma instância **`e2-micro`** (2 vCPUs compartilhadas, 1GB RAM) **totalmente gratuita** mensalmente (regiões us-central1, us-east1 ou us-west1). Como o consumo das aplicações em demonstração é pontual, é possível rodar todas lá ajustando os limites de memória ou ativando memória swap (SWAP de 2GB a 4GB).

#### Estimativa de Custo Mensal (Alternativa A)

| Componente | Provedor / Detalhes | Custo Mensal |
| :--- | :--- | :--- |
| **Hospedagem (VM/VPS)** | GCP `e2-micro` (Free Tier) <br> *Alternativa paga: DigitalOcean Basic 4GB RAM ($24/mês) ou Hetzner CX22 ($4/mês)* | **$0,00** (GCP) <br> ou ~$4,00 a $24,00 |
| **Banco de Dados** | PostgreSQL rodando localmente na própria VM via contêiner Docker (com volume persistente) | **$0,00** |
| **Redis** | Redis rodando localmente na própria VM via contêiner Docker (para o Rack Plus) | **$0,00** |
| **Domínio Personalizado** | Registro de domínio `.com` ou `.com.br` (ex: `meustccs.com.br`) para criar subdomínios | ~$10,00 / ano (~$0,80/mês) |
| **Certificados SSL** | Let's Encrypt (Automático via Traefik ou Certbot) | **$0,00** |
| **Gemini API** | Google AI Studio (Free Tier limitado a 15 RPM / 1M TPM) | **$0,00** |
| **TOTAL ESTIMADO** | **Hospedagem Gratuita GCP + Domínio próprio** | **R$ 4,00 a R$ 6,00 / mês** |

> [!TIP]
> **Por que esta é a melhor opção?**
> Além de ser extremamente barata (quase 100% gratuita no GCP Free Tier), permite centralizar a administração e as atualizações. Um único comando `docker compose up -d` sobe toda a infraestrutura de TCCs de uma só vez.

---

### Alternativa B: PaaS Serverless (Render.com + Neon.tech + Upstash)
Usar plataformas de nuvem gerenciadas onde o código é implantado de forma isolada, escalando até zero quando não estiver em uso.

* **Render.com**: Permite implantar web services gratuitos.
  * *Limitação*: Se ficarem 15 minutos sem receber requisições, entram em modo de suspensão (cold start) e demoram cerca de 50 segundos para responder à primeira requisição seguinte.
* **Neon.tech / Supabase**: Oferece bancos de dados PostgreSQL gratuitos com excelente performance.
* **Upstash**: Oferece instância Redis gratuita (com limite de comandos/dia) excelente para o Channels do `repo-rack-plus`.

#### Estimativa de Custo Mensal (Alternativa B)

| Componente | Provedor / Detalhes | Custo Mensal |
| :--- | :--- | :--- |
| **Web Services (Web App/API)** | Render.com (Até 5 Web Services no plano gratuito) <br> *Hospedar Easy English, Edu Hub, Enlace Backend, MyServer, Skillex Backend* | **$0,00** |
| **Estáticos (Frontends React)** | Render Static Sites ou Vercel (Hospedar Frontends de Enlace e Skillex) | **$0,00** |
| **Banco de Dados** | Neon.tech / Supabase (Bancos PostgreSQL gratuitos individuais ou único compartilhado) | **$0,00** |
| **Redis** | Upstash Redis (Plano Free - excelente para o Rack Plus Channels Layer) | **$0,00** |
| **TOTAL ESTIMADO** | **Nuvem PaaS 100% Gratuita (com Cold Starts)** | **$0,00 (Gratuito)** |

> [!WARNING]
> **Aviso sobre Limitações do Render Free Tier:**
> O Render possui um limite mensal de horas de uso gratuitas para Web Services (750 horas compartilhadas entre todos os seus serviços gratuitos na conta). Se você implantar 5 serviços ativos simultaneamente, o seu saldo de horas gratuitas esgotará em cerca de **6 dias** no mês. Portanto, para hospedar os 6 serviços de forma permanente, você precisará atualizar alguns para o plano Hobby (~$7/mês por serviço) ou usar contas separadas.

---

### Alternativa C: Google Cloud Serverless Puro (Cloud Run + Supabase)
Utilizar o **Google Cloud Run** para implantar os contêineres Docker das aplicações de forma serverless.

* **Cloud Run**: Escala a CPU/Memória para zero instantaneamente quando não há tráfego, cobrando estritamente por milissegundo de execução. O plano gratuito inclui 2 milhões de requisições por mês.
* **Banco de Dados (Cloud SQL)**: O Cloud SQL oficial do GCP é muito caro para demonstração (~$10/mês no mínimo por uma instância muito básica). Recomendamos usar bancos PostgreSQL gratuitos externos (como Neon ou Supabase) conectados às instâncias do Cloud Run.

#### Estimativa de Custo Mensal (Alternativa C)

| Componente | Provedor / Detalhes | Custo Mensal |
| :--- | :--- | :--- |
| **Serviço de Compute** | GCP Cloud Run (6 contêineres implantados configurados para escalar a 0 instâncias) | **$0,00 a $2,00** (dentro do limite gratuito se o tráfego for apenas para demonstração) |
| **Banco de Dados** | Supabase ou Neon.tech (PostgreSQL Gratuito) | **$0,00** |
| **Redis (Rack Plus)** | Upstash Redis (Plano Free) ou contêiner Redis no Cloud Run | **$0,00** |
| **TOTAL ESTIMADO** | **Serverless Híbrido GCP + Bancos Gratuitos** | **R$ 0,00 a R$ 10,00 / mês** |

---

## 3. Resumo Comparativo para Tomada de Decisão

| Critério | Alternativa A (VPS + Docker) | Alternativa B (Render Free) | Alternativa C (GCP Cloud Run) |
| :--- | :--- | :--- | :--- |
| **Custo Mensal** | **Quase Zero** (~R$ 5/mês de domínio ou VM Hetzner de R$ 25/mês) | **Zero ($0.00)** | **Híbrido de R$ 0 a R$ 10/mês** |
| **Desempenho** | **Excelente**. Sem lentidão ao carregar (sem "cold starts"). | **Regular**. A primeira requisição após 15 minutos de inatividade demora ~1 minuto. | **Bom**. "Cold start" moderado de ~5 a 10 segundos na primeira requisição. |
| **Complexidade** | **Média**. Requer configurar o Docker e o Proxy Reverso uma única vez. | **Baixa**. Interface gráfica simples de arrastar e soltar do Render. | **Média**. Requer comandos `gcloud` ou painel do GCP. |
| **Limites Oficiais** | Sem limites além do hardware da máquina. | Limite de 750 horas mensais compartilhadas (esgota rápido com 6 apps). | 2 Milhões de requisições gratuitas (virtualmente infinito para demonstração). |

### Recomendação do Assistente:
Para uma demonstração acadêmica e de avaliação profissional de TCCs sem surpresas de cobrança e com carregamento rápido e fluido dos sistemas dos alunos, o uso da **Alternativa A (VPS Único)** ou da **Alternativa C (GCP Cloud Run com banco gratuito)** são as opções ideais.
Se você possuir uma conta GCP ativa, configurar os serviços no **Cloud Run** com instâncias que escalam até zero dará um toque extremamente moderno e profissional aos deploys.
