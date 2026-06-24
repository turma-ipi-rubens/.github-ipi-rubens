# Guia de Deploy Cloud - Rack Plus

## 1. Secrets adicionais
* `REDIS_URL`: URL do Redis para Channels.

## 2. Deploy
1. Use **Railway** (suporta containers com Daphne e Redis integrados).
2. Start command: `daphne -b 0.0.0.0 -p 8000 core.asgi:application`
