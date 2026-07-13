import Link from 'next/link'
import { Zap } from 'lucide-react'

export function SiteFooter() {
  return (
    <footer className="border-t bg-card">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-10 md:flex-row md:items-center md:justify-between md:px-6">
        <div className="flex items-center gap-2">
          <span className="flex size-7 items-center justify-center rounded-md bg-sidebar-primary">
            <Zap className="size-3.5 text-sidebar-primary-foreground" aria-hidden="true" />
          </span>
          <span className="text-sm font-semibold">OfertaBot</span>
          <span className="text-sm text-muted-foreground">
            — Ofertas do Mercado Livre no Telegram
          </span>
        </div>
        <nav className="flex items-center gap-6" aria-label="Rodapé">
          <Link
            href="/ofertas"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Ofertas
          </Link>
          <Link
            href="/admin"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Painel
          </Link>
          <a
            href="https://github.com/CluthPh/oferta"
            target="_blank"
            rel="noreferrer"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            GitHub
          </a>
        </nav>
      </div>
    </footer>
  )
}
