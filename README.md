# MUCAMBO NEXUS - Sistema Autônomo de Arbitragem 24/7 (Ativos Intangíveis)

Sistema autônomo de alta performance que monitora oportunidades globais de compra e venda de **ativos intangíveis de valor** (100% digitais, sem estoque físico e sem capital imobilizado), operando 24 horas por dia com execução **Just-in-Time (JIT)** e adaptação automática de idioma e moeda por localidade.

---

## ⚡ Como Funciona a Mecânica (Zero Risco de Estoque)

1. **Varredura Global 24/7 (`Hunters`)**:
   - O robô vasculha o mundo continuamente em busca de ativos intangíveis subprecificados:
     - **Domínios Web de Alto Valor**: Nomes expirados ou sob leilão com autoridade SEO e demanda comercial (.ai, .io, .com, .app).
     - **Serviços Digitais & IA (Drop-Servicing)**: Relatórios de inteligência B2B, auditorias e enriquecimento de dados procurados por empresas e executados sob demanda via APIs especializadas por centavos.
     - **Spreads de Mercados Preditivos**: Discrepâncias de probabilidade entre livros de ofertas globais.
2. **Vitrine & Catálogo Just-in-Time**:
   - Os ativos aprovados são expostos no mercado global com margem líquida calculada (média de 40% a 90%).
   - O sistema **NÃO** compra o ativo antes de haver um comprador garantido.
3. **Liquidação Sob Demanda**:
   - Assim que uma ordem de compra é recebida (ou quando um comprador da rede fecha o pedido), o robô adquire o ativo na fonte em milissegundos e entrega instantaneamente ao cliente final, creditando o lucro líquido (*spread*) no livro contábil (*Ledger*).
4. **Auto-Adaptação de Idioma e Moeda**:
   - Detecta o país/idioma do visitante (Português, Inglês, Espanhol, etc.).
   - Converte valores cambiais em tempo real (R$ BRL, $ USD, € EUR, £ GBP, ¥ JPY).
   - Traduz automaticamente a descrição e os termos do ativo para o mercado de destino.

---

## 🚀 Como Iniciar o Sistema

### Opção 1: Via NPM (Recomendado)
No terminal dentro da pasta do projeto, execute:
```bash
npm start
```
*Ele detectará o ambiente, iniciará o sistema autônomo 24/7 e abrirá o navegador automaticamente em `http://localhost:8000`.*

### Opção 2: Clique Duplo (Windows)
Dê dois cliques no arquivo:
```
start.bat
```

### Opção 3: Linha de Comando Python
```powershell
py main.py
```
Acesse no seu navegador: **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 Como Rodar os Testes Automatizados
```powershell
py tests/test_arbitrage.py
```

---

## 📁 Estrutura do Projeto

```
MUCAMBO/
├── config.py                  # Parâmetros gerais, margens mínimas, moedas
├── main.py                    # Ponto de entrada do sistema
├── start.bat                  # Inicializador rápido Windows
├── core/
│   ├── localization.py        # Motor de adaptação de idioma (i18n) e moedas
│   ├── models.py              # Modelos de dados (Oportunidades, Ordens, Ledger)
│   ├── database.py            # Banco SQLite local persistente
│   └── scheduler.py           # Loop 24/7 assíncrono não bloqueante
├── hunters/
│   ├── base_hunter.py         # Interface padrão de varredura
│   ├── domain_hunter.py       # Caçador de domínios expirados de valor
│   ├── digital_service_hunter.py # Caçador de micro-serviços digitais e IA
│   └── prediction_hunter.py   # Caçador de spreads de previsão
├── execution/
│   ├── arbitrage_engine.py    # Motor de validação de spread e risco
│   └── fulfillment.py         # Compra na fonte e entrega Just-in-Time
├── web/
│   ├── app.py                 # FastAPI backend com WebSockets
│   ├── static/                # CSS cyberpunk/fintech e JavaScript reativo
│   └── templates/             # Template HTML do Dashboard
└── tests/
    └── test_arbitrage.py      # Suíte de verificação automatizada
```
