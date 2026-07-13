'use client'

import Link from 'next/link'
import { Zap } from 'lucide-react'

import { Button } from '@/components/ui/button'

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-sidebar-primary">
            <Zap className="size-4 text-sidebar-primary-foreground" aria-hidden="true" />
          </span>
          <span className="text-lg font-semibold tracking-tight">OfertaBot</span>
        </Link>
        <nav className="hidden items-center gap-6 md:flex" aria-label="Navegação principal">
          <a
            href="#como-funciona"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Como funciona
          </a>
          <a
            href="#recursos"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Recursos
          </a>
          <Link
            href="/ofertas"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Ofertas
          </Link>
        </nav>
        <div className="flex items-center gap-2">
          <Button variant="ghost" nativeButton={false} render={<Link href="/admin" />}>
            Painel
          </Button>
          <Button nativeButton={false} render={<Link href="/ofertas" />}>
            Ver ofertas
          </Button>
        </div>
      </div>
    </header>
  )
}
