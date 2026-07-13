# Architecture

O projeto separa dominio e infraestrutura.

- Marketplace provider: busca e normaliza dados externos para `ProductCandidate`.
- Product service: grava produto, vendedor e historico de preco.
- Offer service: aplica filtros e calcula score.
- Affiliate provider: resolve link por URL manual, banco ou CSV pendente.
- Publication service: aplica deduplicacao por `product_id + channel_id` e publica.
- Telegram publisher: envia foto, legenda HTML e botao inline.
- FastAPI: exposicao administrativa sem frontend.

SQLite e o padrao. PostgreSQL funciona alterando `DATABASE_URL`.

Timestamps sao gravados em UTC. Repostagem considera queda minima, janela de horas e
modo `repost`, `edit` ou `ignore`.

