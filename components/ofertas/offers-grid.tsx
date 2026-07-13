'use client'

import * as React from 'react'
import Image from 'next/image'
import { ExternalLink, Flame, PackageSearch, Search, Truck } from 'lucide-react'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'
import { products, formatBRL } from '@/lib/demo-data'

const niches = ['Todos', 'Áudio', 'Wearables', 'Casa & Cozinha', 'Informática', 'Esportes', 'TV & Vídeo']

export function OffersGrid() {
  const [search, setSearch] = React.useState('')
  const [niche, setNiche] = React.useState('Todos')

  const filtered = products.filter((product) => {
    const matchesSearch = product.title.toLowerCase().includes(search.toLowerCase())
    const matchesNiche = niche === 'Todos' || product.niche === niche
    return matchesSearch && matchesNiche
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4">
        <div className="relative max-w-md">
          <Search
            className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />
          <Input
            placeholder="Buscar oferta..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Buscar oferta"
          />
        </div>
        <ToggleGroup
          value={[niche]}
          onValueChange={(value) => {
            const next = Array.isArray(value) ? value[value.length - 1] : value
            if (next) setNiche(next)
          }}
          className="flex-wrap justify-start"
          aria-label="Filtrar por nicho"
        >
          {niches.map((item) => (
            <ToggleGroupItem key={item} value={item} className="px-3">
              {item}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      {filtered.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <PackageSearch />
            </EmptyMedia>
            <EmptyTitle>Nenhuma oferta encontrada</EmptyTitle>
            <EmptyDescription>
              Tente outro termo de busca ou selecione um nicho diferente.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((product) => (
            <Card key={product.id} className="group overflow-hidden pt-0">
              <div className="relative bg-white p-6">
                <Image
                  src={product.image || '/placeholder.svg'}
                  alt={product.title}
                  width={300}
                  height={300}
                  className="mx-auto aspect-square w-full max-w-44 object-contain transition-transform duration-300 group-hover:scale-105"
                />
                <Badge className="absolute left-3 top-3 bg-success text-success-foreground">
                  -{product.discount}%
                </Badge>
                {product.score >= 85 && (
                  <Badge className="absolute right-3 top-3 bg-warning text-warning-foreground">
                    <Flame className="size-3" aria-hidden="true" />
                    Imperdível
                  </Badge>
                )}
              </div>
              <CardContent className="flex flex-1 flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-muted-foreground">{product.store}</span>
                  <h3 className="line-clamp-2 text-sm font-medium leading-snug">
                    {product.title}
                  </h3>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-xl font-bold tabular-nums">
                    {formatBRL(product.price)}
                  </span>
                  <span className="text-sm text-muted-foreground line-through tabular-nums">
                    {formatBRL(product.oldPrice)}
                  </span>
                </div>
                {product.freeShipping && (
                  <span className="flex items-center gap-1.5 text-xs font-medium text-success">
                    <Truck className="size-3.5" aria-hidden="true" />
                    Frete grátis
                  </span>
                )}
                <Button
                  className="mt-auto w-full"
                  nativeButton={false}
                  render={
                    <a
                      href={product.affiliateLink}
                      target="_blank"
                      rel="noreferrer"
                      aria-label={`Ver oferta de ${product.title} no Mercado Livre`}
                    />
                  }
                >
                  Ver oferta
                  <ExternalLink data-icon="inline-end" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
