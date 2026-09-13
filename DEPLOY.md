# Guia de Hospedagem Online 24/7 - MUCAMBO NEXUS

Para que o robô opere **24 horas por dia, 7 dias por semana pelo mundo todo sem depender do seu computador ficar ligado**, você deve hospedá-lo em um servidor na nuvem.

Abaixo estão as **3 melhores opções** (do mais fácil ao mais avançado):

---

## 🌟 OPÇÃO 1: Render.com ou Railway (Mais Rápida e Fácil - Recomendada)
*Ideal para começar sem gerenciar servidores Linux. Oferece HTTPS/SSL grátis e domínio online automático.*

### Passo a passo no Render:
1. Crie uma conta gratuita em [render.com](https://render.com).
2. Suba a pasta deste projeto (`MUCAMBO`) para o seu GitHub (repositório público ou privado).
3. No painel do Render, clique em **"New +" -> "Web Service"**.
4. Conecte o repositório do GitHub.
5. O Render detectará automaticamente o arquivo [`render.yaml`](file:///c:/Users/mlesa/OneDrive/Desktop/MUCAMBO/render.yaml) e [`requirements.txt`](file:///c:/Users/mlesa/OneDrive/Desktop/MUCAMBO/requirements.txt):
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
6. Em **Environment Variables**, adicione suas chaves do arquivo `.env`:
   - `SIMULATION_MODE`: `false` (para modo real)
   - `STRIPE_SECRET_KEY`: `sua_chave_stripe`
   - `OPENAI_API_KEY`: `sua_chave_openai`
   - etc.
7. Clique em **Deploy Web Service**.
8. Pronto! Em 2 minutos seu sistema estará online com link público seguro:
   👉 `https://mucambo-nexus.onrender.com`

---

## 🐳 OPÇÃO 2: Servidor VPS Próprio com Docker (DigitalOcean / Hetzner / AWS)
*Ideal para escala profissional, alta velocidade e controle total.*

1. Contrate uma VPS Linux básica (Ubuntu 22.04/24.04) na Hetzner (a partir de €3.50/mês) ou DigitalOcean (\$4/mês).
2. Conecte na sua VPS via SSH:
   ```bash
   ssh root@ip_do_seu_servidor
   ```
3. Instale o Docker e Docker Compose:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
4. Clone ou copie a pasta do projeto para a VPS.
5. Inicie o sistema 24/7 em segundo plano com reinício automático:
   ```bash
   docker compose up -d
   ```
6. O sistema já estará operando 24 horas por dia, sem parar mesmo se a conexão cair.

---

## ⚡ OPÇÃO 3: Testar Online Imediatamente sem Servidor (Cloudflare Tunnel)
Se quiser colocar o sistema online no mundo **agora mesmo** a partir da sua máquina para testar com clientes reais:

1. Baixe o utilitário oficial gratuito da Cloudflare (`cloudflared`):
   ```powershell
   winget install Cloudflare.cloudflared
   ```
2. Execute o túnel na porta 8000:
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
3. A Cloudflare gerará um link público internacional com HTTPS gratuito:
   👉 `https://seu-link-aleatorio.trycloudflare.com`
4. Qualquer pessoa no mundo poderá acessar o seu painel e efetuar compras!
