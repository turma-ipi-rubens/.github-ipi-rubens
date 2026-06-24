# Plano de Testes Unitários - Easy English

O objetivo é garantir a integridade dos flashcards e o registro de sessões de estudo.

## Escopo dos Testes
1. **Modelo `Flashcard`:** Validação de campos obrigatórios, escolha de baralhos e valores padrão.
2. **Modelo `EstudoSessao`:** Registro correto de acertos, erros e cálculo da taxa de acerto.
3. **Serviços de Dashboard:** Retorno dos contadores corretos do usuário logado.

## Estrutura Recomendada
Os testes devem ser rodados com `python manage.py test`.
