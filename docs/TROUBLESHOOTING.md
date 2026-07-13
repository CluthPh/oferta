# Troubleshooting

## API Mercado Livre 403

O cliente registra o erro, abre circuit breaker depois de falhas repetidas e tenta o
fallback web quando possivel. Nao ha bypass de protecao.

## Telegram 429

O cliente respeita `retry_after` e tenta novamente com backoff.

## Sem imagem

O publicador envia texto com botao. Se o envio por URL falhar, tenta baixar a imagem,
validar `Content-Type` e tamanho, enviar arquivo temporario e remover o arquivo.

## Duplicidade

A deduplicacao usa `product_id + channel_id`. Repostagem ocorre somente por queda de
preco, prazo configurado, falha anterior ou modo de edicao.

## Produto sem afiliado

O produto entra em `data/pending_affiliate_links.csv`. Com
`POST_WITHOUT_AFFILIATE_LINK=false`, ele nao e publicado.

