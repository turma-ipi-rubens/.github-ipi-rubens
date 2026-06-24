# Plano de Testes Unitários - EduHub

Foco no processo de avaliação e correção de tarefas usando IA.

## Escopo dos Testes
1. **Integração com IA:** Testar `corrigir_com_ia` mockando a resposta da API do Gemini para evitar cobranças reais.
2. **Fallback de Erro:** Verificar se erros da API (como HTTP 503) incrementam a contagem de tentativas de correção.
