import type { Metadata } from 'next'
import { Send } from 'lucide-react'

import { SiteHeader } from '@/components/landing/site-header'
import { SiteFooter } from '@/components/landing/site-footer'
import { Button } from '@/components/ui/button'
import { OffersGrid } from '@/components/ofertas/offers-grid'

export const metadata: Metadata = {
  title: 'Ofertas — OfertaBot',
  description:
    'As melhores ofertas do Mercado Livre encontradas pelo OfertaBot, atualizadas ao longo do dia.',
}

export default function OfertasPage() {
  return (
    <div className="flex min-h-svh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <section className="border-b bg-card">
          <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-10 md:flex-row md:items-end md:justify-between md:px-6 md:py-14">
            <div className="flex max-w-xl flex-col gap-2">
              <h1 className="text-balance text-3xl font-bold tracking-tight md:text-4xl">
                Ofertas de hoje
              </h1>
              <p className="text-pretty leading-relaxed text-muted-foreground">
                Selecionadas automaticamente pelo robô com base em desconto real, histórico de
                preço e reputação da loja.
              </p>
            </div>
            <Button
              variant="outline"
              nativeButton={false}
              render={<a href="https://t.me/ofertasbr" target="_blank" rel="noreferrer" />}
            >
              <Send data-icon="inline-start" />
              Receber no Telegram
            </Button>
          </div>
        </section>
        <section className="mx-auto w-full max-w-6xl px-4 py-8 md:px-6 md:py-12">
          <OffersGrid />
        </section>
      </main>
      <SiteFooter />
    </div>
  )
}
