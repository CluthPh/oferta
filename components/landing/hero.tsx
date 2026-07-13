import Link from 'next/link'
import Image from 'next/image'
import { ArrowRight, BadgePercent, Send } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatBRL, products } from '@/lib/demo-data'

export function Hero() {
  const featured = products.slice(0, 3)

  return (
    <section className="relative overflow-hidden bg-sidebar text-sidebar-foreground">
      <div className="mx-auto grid w-full max-w-6xl grid-cols-1 items-center gap-12 px-4 py-16 md:px-6 md:py-24 lg:grid-cols-2">
        <div className="flex flex-col items-start gap-6">
          <Badge className="bg-sidebar-accent text-sidebar-accent-foreground">
            <Send className="size-3" aria-hidden="true" />
            Publicação automática no Telegram
          </Badge>
          <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight md:text-5xl lg:text-6xl">
            As melhores ofertas do Mercado Livre,{' '}
            <span className="text-sidebar-primary">encontradas por robô</span>
          </h1>
          <p className="max-w-xl text-pretty text-lg leading-relaxed text-sidebar-foreground/70">
            O OfertaBot monitora preços 24 horas por dia, calcula um score de qualidade para cada
            oferta e publica automaticamente as melhores no seu canal do Telegram.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              size="lg"
              className="bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
              nativeButton={false}
              render={<Link href="/ofertas" />}
            >
              Ver ofertas de hoje
              <ArrowRight data-icon="inline-end" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-sidebar-border bg-transparent text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              nativeButton={false}
              render={<Link href="/admin" />}
            >
              Conhecer o painel
            </Button>
          </div>
          <dl className="mt-2 flex flex-wrap gap-8">
            <div className="flex flex-col gap-1">
              <dt className="text-sm text-sidebar-foreground/60">Ofertas publicadas</dt>
              <dd className="text-2xl font-bold tabular-nums">1.284</dd>
            </div>
            <div className="flex flex-col gap-1">
              <dt className="text-sm text-sidebar-foreground/60">Economia média</dt>
              <dd className="text-2xl font-bold tabular-nums">36%</dd>
            </div>
            <div className="flex flex-col gap-1">
              <dt className="text-sm text-sidebar-foreground/60">Monitoramento</dt>
              <dd className="text-2xl font-bold tabular-nums">24/7</dd>
            </div>
          </dl>
        </div>

        <div className="flex flex-col gap-3" aria-label="Exemplos de ofertas encontradas">
          {featured.map((product, index) => (
            <div
              key={product.id}
              className={
                index === 1
                  ? 'flex items-center gap-4 rounded-xl border border-sidebar-border bg-card p-4 text-card-foreground shadow-lg lg:translate-x-8'
                  : 'flex items-center gap-4 rounded-xl border border-sidebar-border bg-card p-4 text-card-foreground shadow-lg'
              }
            >
              <Image
                src={product.image || '/placeholder.svg'}
                alt={product.title}
                width={64}
                height={64}
                className="size-16 shrink-0 rounded-lg border bg-white object-cover"
              />
              <div className="flex min-w-0 flex-1 flex-col gap-1">
                <span className="truncate text-sm font-medium">{product.title}</span>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold tabular-nums">
                    {formatBRL(product.price)}
                  </span>
                  <span className="text-sm text-muted-foreground line-through tabular-nums">
                    {formatBRL(product.oldPrice)}
                  </span>
                </div>
              </div>
              <Badge className="shrink-0 bg-success text-success-foreground">
                <BadgePercent className="size-3" aria-hidden="true" />-{product.discount}%
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
