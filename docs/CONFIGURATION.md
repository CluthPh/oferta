# Configuration

Variaveis principais no `.env`:

- `TELEGRAM_BOT_TOKEN`: token do BotFather.
- `DATABASE_URL`: padrao `sqlite:///data/offers.db`.
- `ADMIN_API_KEY`: chave exigida por endpoints de escrita.
- `DRY_RUN`: `true` por padrao.
- `POST_WITHOUT_AFFILIATE_LINK`: permite usar link comum quando nao ha afiliado.
- `MERCADOLIVRE_ACCESS_TOKEN`: opcional para API oficial.
- `NICHES_CONFIG_PATH`: caminho do YAML.
- `SCAN_INTERVAL_MINUTES`: intervalo do worker continuo.
- `RUN_SCAN_ON_STARTUP`: executa um ciclo assim que o worker abre.

`data/niches.yml`:

- `telegram.chat_ids`: canais ou grupos.
- `searches`: consultas automaticas.
- `manual_products`: URLs monitoradas.
- `publication`: limite por ciclo, janela de repostagem e modo de preco.

Campos de texto enviados ao Telegram sao escapados em HTML.
