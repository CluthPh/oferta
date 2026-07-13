# Painel administrativo

Suba a API:

```powershell
.\scripts\run.ps1
```

Acesse:

```text
http://127.0.0.1:8000/admin
```

Para acoes de escrita, defina `ADMIN_API_KEY` no `.env` e informe a mesma chave no campo do
painel. Leituras basicas como dashboard, produtos, publicacoes e pendencias continuam
disponiveis sem chave.

## Recursos

- Dashboard com contadores, ultimos ciclos e eventos recentes.
- Validacao de `.env`, banco e `data/niches.yml`.
- Scan manual por `POST /jobs/scan`.
- Login por sessao/cookie usando `ADMIN_API_KEY`.
- Lista de produtos com filtros, marcar produto como ignorado e previa da mensagem do Telegram.
- Grafico simples de historico de preco por produto.
- Botao para publicar um produto especifico imediatamente.
- Fila de aprovacao com aprovar, rejeitar e publicar.
- CRUD basico de links afiliados.
- Importacao/exportacao CSV de links afiliados.
- Visualizacao de pendencias em `data/pending_affiliate_links.csv`.
- Edicao visual de nichos e edicao validada de `data/niches.yml`, com backup `.bak`.
- Ajustes de execucao no `.env`: `DRY_RUN`, intervalo, aprovacao obrigatoria e fontes.
- Diagnostico de token/canal do Telegram.
- Relatorio das ultimas 24h.
- Leitura dos logs `application.log` e `errors.log`.

## Endpoints principais

```text
GET  /admin
GET  /dashboard
GET  /config/validate
GET  /config/niches
PUT  /config/niches
GET  /settings/runtime
PATCH /settings/runtime
GET  /sources
GET  /scan-runs
GET  /products
GET  /products/{product_id}/price-history
POST /products/{product_id}/publish
GET  /publications
GET  /offers/pending
POST /offers/publish-now
GET  /approvals
POST /approvals/{approval_id}/approve
POST /approvals/{approval_id}/reject
POST /approvals/{approval_id}/publish
GET  /reports/daily
POST /telegram/test
GET  /affiliate-links
POST /offers/preview
PUT  /config/raw
POST /affiliate-links
POST /affiliate-links/import
GET  /affiliate-links/export
```

## Publicacao segura

O ciclo agora respeita `publication.max_posts_per_cycle` e
`publication.seconds_between_posts`. Produtos marcados como ignorados no painel nao sao
republicados em novas coletas. O servico tambem bloqueia duplicidade do mesmo produto no
mesmo ciclo.

Se `REQUIRE_APPROVAL=true`, ofertas aprovadas pelo score entram na fila e nao sao
publicadas automaticamente. Com `REQUIRE_APPROVAL=false`, a fila continua recebendo os
registros, mas o fluxo automatico segue publicando.
