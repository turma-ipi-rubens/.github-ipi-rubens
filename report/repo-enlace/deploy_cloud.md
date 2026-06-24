# Guia de Deploy Cloud - Enlace

## 1. Variáveis
* **Backend:** `DATABASE_URL`, `JWT_SECRET`, `PORT=3000`.
* **Frontend:** `VITE_API_URL` (apontando para a URL pública do seu Backend).

## 2. Deploy
1. Suba o **Backend** no Render como Web Service (Dockerfile incluso).
2. Suba o **Frontend** no Netlify, Vercel ou Render Static Site.
