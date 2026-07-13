'use client'

import * as React from 'react'
import Image from 'next/image'
import { Search, ExternalLink, PackageSearch } from 'lucide-react'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'
import { ScoreBadge } from '@/components/admin/score-badge'
import { products, formatBRL, type ProductStatus } from '@/lib/demo-data'

const statusItems = [
  { value: 'todos', label: 'Todos os status' },
  { value: 'pendente', label: 'Pendente' },
  { value: 'publicado', label: 'Publicado' },
  { value: 'monitorando', label: 'Monitorando' },
  { value: 'rejeitado', label: 'Rejeitado' },
]

const statusConfig: Record<ProductStatus, { label: string; className: string }> = {
  publicado: { label: 'Publicado', className: 'bg-success/15 text-success' },
  pendente: { label: 'Pendente', className: 'bg-warning/25 text-warning-foreground' },
  rejeitado: { label: 'Rejeitado', className: 'bg-destructive/10 text-destructive' },
  monitorando: { label: 'Monitorando', className: 'bg-muted text-muted-foreground' },
}

export function ProductsTable() {
  const [search, setSearch] = React.useState('')
  const [status, setStatus] = React.useState<string>('todos')

  const filtered = products.filter((product) => {
    const matchesSearch = product.title.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = status === 'todos' || product.status === status
    return matchesSearch && matchesStatus
  })

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search
            className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />
          <Input
            placeholder="Buscar produto..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Buscar produto"
          />
        </div>
        <Select
          items={statusItems}
          value={status}
          onValueChange={(v) => setStatus(v ?? 'todos')}
        >
          <SelectTrigger className="w-full sm:w-44" aria-label="Filtrar por status">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {statusItems.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      {filtered.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <PackageSearch />
            </EmptyMedia>
            <EmptyTitle>Nenhum produto encontrado</EmptyTitle>
            <EmptyDescription>
              Ajuste a busca ou o filtro de status para ver outros produtos.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : (
        <Card>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Produto</TableHead>
                  <TableHead className="hidden md:table-cell">Nicho</TableHead>
                  <TableHead>Preço</TableHead>
                  <TableHead className="hidden lg:table-cell">Desconto</TableHead>
                  <TableHead className="hidden sm:table-cell">Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">
                    <span className="sr-only">Ações</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((product) => {
                  const st = statusConfig[product.status]
                  return (
                    <TableRow key={product.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Image
                            src={product.image || '/placeholder.svg'}
                            alt={product.title}
                            width={40}
                            height={40}
                            className="size-10 shrink-0 rounded-md border bg-card object-cover"
                          />
                          <div className="flex min-w-0 flex-col">
                            <span className="max-w-48 truncate text-sm font-medium lg:max-w-80">
                              {product.title}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {product.id} · {product.store}
                            </span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="hidden md:table-cell">
                        <Badge variant="outline">{product.niche}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="text-sm font-medium tabular-nums">
                            {formatBRL(product.price)}
                          </span>
                          <span className="text-xs text-muted-foreground line-through tabular-nums">
                            {formatBRL(product.oldPrice)}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="hidden lg:table-cell">
                        <Badge variant="secondary" className="text-success">
                          -{product.discount}%
                        </Badge>
                      </TableCell>
                      <TableCell className="hidden sm:table-cell">
                        <ScoreBadge score={product.score} />
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={st.className}>
                          {st.label}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          nativeButton={false}
                          render={
                            <a
                              href={product.affiliateLink}
                              target="_blank"
                              rel="noreferrer"
                              aria-label={`Abrir link de afiliado de ${product.title}`}
                            />
                          }
                        >
                          <ExternalLink />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
