# Relatório de Avaliação - Projeto Rack Plus

## 1. Identificação
* **Repositório:** `repo-rack-plus`
* **Branch Ativa:** `US06-QA-T02`
* **Tema do Projeto:** Sistema de monitoramento e telemetria de infraestrutura de TI (Rack Plus), composto por um portal de gerenciamento web e um agente coletor local para sistemas Windows.

## 2. Visão Geral da Arquitetura e Implementação
O projeto está dividido em:
* **Backend e Painel Web:** Desenvolvido em **Django**, incluindo suporte a **WebSockets (Django Channels)** via `consumers.py` e `routing.py` para atualizações de telemetria em tempo real nas telas do painel.
* **Agente de Telemetria (`agente`):** Um script em Python independente contendo um coletor (`collector.py`) que consome dados do sistema operacional e hardware através das bibliotecas `psutil` e APIs nativas do Windows (`winreg`), além de um wrapper de serviço (`service_wrapper.py`) para execução em segundo plano.

## 3. Avaliação Técnica
* **Implementação do Agente:**
  * Excelente manuseio de APIs nativas do Windows via registro do sistema (`winreg`) para obter o nome real do processador, versão do sistema operacional (tratando retrocompatibilidade do Windows 11 reportado como Windows 10) e serial do BIOS.
  * Presença de scripts instaladores robustos (`install.ps1`, `instalar_servico.bat`, `instalar_usuario.bat`) e script de empacotamento (`build_dist.ps1`) com PyInstaller para gerar o executável final do agente.
  * O coletor está preparado para rodar silenciosamente em segundo plano, ocultando janelas de subprocessos (`dwFlags |= subprocess.STARTF_USESHOWWINDOW`).
* **Sincronização em Tempo Real:**
  * O painel web possui suporte a WebSockets/Django Channels, permitindo que a telemetria recebida seja transmitida instantaneamente para a interface do usuário.

## 4. Sugestões de Melhoria e Feedbacks
* **Portabilidade:** Atualmente, a detecção de serial de hardware (`get_hw_serial`) e nome do SO faz chamadas muito acopladas ao ecossistema Windows (`winreg`, WMIC). Caso o sistema precise futuramente suportar agentes em Linux/macOS, a lógica de coleta de identificador único e SO no `collector.py` precisará de condicionais baseadas em `platform.system()`.
* **Tratamento de Exceções de Permissão:** Ler chaves de registro do Windows (`winreg`) às vezes requer privilégios elevados (Administrator). Garantir que o agente avise amigavelmente ou registre um log específico se for iniciado sem privilégios administrativos.

---
*Relatório gerado automaticamente em 2026-06-23 pelo assistente AI Antigravity.*
