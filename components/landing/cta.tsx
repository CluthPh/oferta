import Link from 'next/link'
import { ArrowRight, Send } from 'lucide-react'

import { Button } from '@/components/ui/button'

export function CTA() {
  return (
    <section className="mx-auto w-full max-w-6xl px-4 py-16 md:px-6 md:py-24">
      <div className="flex flex-col items-center gap-6 rounded-2xl bg-sidebar px-6 py-14 text-center text-sidebar-foreground md:px-12">
        <div className="flex size-12 items-center justify-center rounded-xl bg-sidebar-primary">
          <Send className="size-6 text-sidebar-primary-foreground" aria-hidden="true" />
        </div>
        <h2 className="max-w-2xl text-balance text-3xl font-bold tracking-tight md:text-4xl">
          Nunca mais perca uma oferta de verdade
        </h2>
        <p className="max-w-xl text-pretty leading-relaxed text-sidebar-foreground/70">
          Acompanhe a vitrine pública ou entre no canal do Telegram para receber as melhores
          ofertas do Mercado Livre assim que forem encontradas.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Button
            size="lg"
            className="bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
            nativeButton={false}
            render={<Link href="/ofertas" />}
          >
            Ver ofertas agora
            <ArrowRight data-icon="inline-end" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-sidebar-border bg-transparent text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            nativeButton={false}
            render={
              <a href="https://t.me/ofertasbr" target="_blank" rel="noreferrer" />
            }
          >
            <Send data-icon="inline-start" />
            Entrar no canal
          </Button>
        </div>
      </div>
    </section>
  )
}
