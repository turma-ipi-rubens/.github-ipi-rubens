# Plano de Testes Unitários - MyServer

## Escopo dos Testes
1. **Controle de Acesso:** Garantir que o endpoint `ServidorViewSet` apenas exiba servidores públicos e autenticados de forma correta.
2. **Serializadores Separados:** Testar se o payload público remove campos como IP, porta e chaves sensíveis.
