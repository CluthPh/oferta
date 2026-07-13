# Oferta Telegram

Sistema em Python para monitorar ofertas do Mercado Livre, aplicar regras por nicho,
resolver links de afiliado e publicar em canais do Telegram. O modo inicial e seguro:
`DRY_RUN=true`, portanto nada e enviado ate voce alterar explicitamente o `.env`.

## Visao geral

O ciclo executa:

1. valida `data/niches.yml`;
2. pesquisa produtos pela API do Mercado Livre e usa fallback web simples quando a API falha;
3. normaliza produto, preco, imagem, vendedor e frete;
4. salva produto e historico de preco no SQLite;
5. calcula desconto e score de oferta;
6. resolve link de afiliado por URL manual ou tabela `affiliate_links`;
7. registra pendencias em `data/pending_affiliate_links.csv`;
8. publica no Telegram ou imprime a previa em dry run.

Nao ha bypass de CAPTCHA, proxy rotativo, login automatico ou criacao falsa de link de
afiliado. Se a coleta for bloqueada, o erro e registrado e o ciclo continua.

## Arquitetura

- `app/marketplaces`: coleta e normalizacao por marketplace.
- `app/services`: regras, descoberta, persistencia e publicacao.
- `app/affiliates`: resolucao de links e CSV de pendencias.
- `app/telegram`: formatacao HTML, cliente Bot API e fallback de imagem.
- `app/database`: SQLAlchemy, modelos e repositorios.
- `app/api`: FastAPI administrativa.
- `app/workers`: ciclo unico e tarefas.

A formula de score soma ate 100 pontos:

- ate 35 por percentual de desconto;
- ate 20 por queda recente de preco;
- 10 por frete gratis;
- 10 por loja oficial;
- ate 15 por aderencia a palavras obrigatorias;
- ate 10 por preco dentro da faixa configurada.

## Requisitos

- Python 3.12 ou superior.
- PowerShell no Windows.
- Token de bot do Telegram para publicacao real.
- Bot como administrador do canal.

## Instalacao no Windows

```powershell
.\scripts\setup.ps1
```

Edite:

- `.env`
- `data\niches.yml`

## Instalacao no Linux

```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
python -m playwright install chromium
cp .env.example .env
cp data/niches.example.yml data/niches.yml
mkdir -p data logs
```

## Docker

```bash
cp .env.example .env
cp data/niches.example.yml data/niches.yml
docker compose up --build
```

## BotFather e canal

1. Crie o bot no BotFather e copie o token para `TELEGRAM_BOT_TOKEN`.
2. Adicione o bot ao canal.
3. Promova o bot a administrador com permissao de postar mensagens.
4. Use `@nome_do_canal` em `telegram.chat_ids` para canais publicos.
5. Para canais privados, use o `chat_id` numerico.

Para descobrir `chat_id`, envie uma mensagem ao canal e consulte:

```bash
curl "https://api.telegram.org/botSEU_TOKEN/getUpdates"
```

## Nichos, pesquisas e URLs

Configure `data/niches.yml`. Cada nicho possui canais, texto, regras de publicacao,
pesquisas e produtos manuais. Produtos manuais podem ter `affiliate_url`; produtos
automaticos precisam de link cadastrado em `/affiliate-links` ou no banco.

CSV de afiliados:

```csv
product_id,canonical_url,affiliate_url,niche,active
MLB123,https://produto.mercadolivre.com.br/MLB-123-produto-_JM,https://link-afiliado,informatica,true
```

Produtos sem link sao registrados em `data/pending_affiliate_links.csv`.

## Executar em modo teste

```powershell
.\scripts\run_once.ps1
```

ou:

```bash
python -m app.main run-once
```

## Painel administrativo

Suba a API e acesse o painel:

```powershell
.\scripts\run.ps1
```

```text
http://127.0.0.1:8000/admin
```

O painel mostra dashboard, validacao, produtos com filtros, grafico de preco, previa de
posts, publicacao manual, fila de aprovacao, links afiliados, pendencias, editor visual de
nichos, ajustes do `.env`, teste do Telegram, relatorio 24h e logs. Para salvar
alteracoes, rodar scan manual ou ver dados protegidos pelo painel, configure
`ADMIN_API_KEY` no `.env`.

Use `REQUIRE_APPROVAL=true` para impedir postagem automatica e obrigar aprovacao manual
no painel.

Detalhes: `docs/ADMIN_PANEL.md`.

## Rodar todos os dias

Para deixar minerando ofertas enquanto o PC estiver ligado:

```powershell
.\scripts\run_worker.ps1
```

Esse comando abre um worker contínuo no terminal. Ele roda um ciclo ao iniciar e repete
conforme `SCAN_INTERVAL_MINUTES` no `.env`.

Exemplos:

```env
SCAN_INTERVAL_MINUTES=60
RUN_SCAN_ON_STARTUP=true
```

Use `SCAN_INTERVAL_MINUTES=1440` para rodar aproximadamente uma vez por dia. Para
postar de verdade, mantenha o worker aberto com `DRY_RUN=false`.

## VSCode

No VSCode, use `Terminal > Run Task...` e escolha:

- `Oferta: worker continuo`
- `Oferta: rodar uma vez`
- `Oferta: API`
- `Oferta: testes`

O worker fica em terminal dedicado e pode ser parado com `Ctrl+C`.

## Iniciar com o Windows

Para abrir um terminal automaticamente quando voce entrar no Windows:

```powershell
.\scripts\install_startup.ps1
```

Para remover:

```powershell
.\scripts\uninstall_startup.ps1
```

## Publicar de verdade

No `.env`:

```env
DRY_RUN=false
TELEGRAM_BOT_TOKEN=seu_token
ADMIN_API_KEY=uma_chave_forte
```

Depois:

```powershell
.\scripts\run.ps1
```

## API

- `GET /health`
- `GET /ready`
- `GET /metrics/summary`
- `GET /products`
- `GET /products/{id}`
- `GET /offers/pending`
- `GET /publications`
- `GET /niches`
- `POST /jobs/scan`
- `POST /jobs/publish`
- `POST /affiliate-links`
- `PATCH /affiliate-links/{id}`
- `POST /products/{id}/publish`
- `POST /products/{id}/ignore`

Endpoints de escrita exigem `X-Admin-Key`.

## 24 horas

Use Docker Compose com `restart: unless-stopped`, systemd no Linux, ou Agendador de
Tarefas no Windows chamando `scripts\run.ps1`.

## Logs

- `logs/application.log`
- `logs/errors.log`

Tokens, cookies e chaves administrativas sao redigidos.

## Backup

Copie:

- `data/offers.db`
- `data/niches.yml`
- `data/pending_affiliate_links.csv`
- `.env` em local seguro

## Testes e qualidade

```powershell
.\scripts\test.ps1
```

ou:

```bash
ruff check .
mypy app tests
pytest
```

## Problemas comuns

- API Mercado Livre retorna 403: configure `MERCADOLIVRE_ACCESS_TOKEN` se sua conta/API exigir token. O fallback web nao tenta contornar bloqueios.
- Bot nao publica: confira token, permissao de administrador e `DRY_RUN=false`.
- Produto sem afiliado: cadastre o link ou use `POST_WITHOUT_AFFILIATE_LINK=true`.
- Configuracao invalida: `/ready` retorna falha e o erro aparece no log.

## Limitacoes

O fallback web depende de JSON-LD publico da pagina. Se houver CAPTCHA, 403 ou pagina
sem dados estruturados, o produto e ignorado naquele ciclo. O sistema nao automatiza o
painel de afiliados.
