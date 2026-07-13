import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ScoreBadge } from '@/components/admin/score-badge'
import { products, formatBRL, type ProductStatus } from '@/lib/demo-data'

const statusVariant: Record<ProductStatus, { label: string; className: string }> = {
  publicado: { label: 'Publicado', className: 'bg-success/15 text-success' },
  pendente: { label: 'Pendente', className: 'bg-warning/25 text-warning-foreground' },
  rejeitado: { label: 'Rejeitado', className: 'bg-destructive/10 text-destructive' },
  monitorando: { label: 'Monitorando', className: 'bg-muted text-muted-foreground' },
}

export function RecentOffers() {
  const recent = products.slice(0, 6)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <div className="flex flex-col gap-1">
          <CardTitle>Ofertas recentes</CardTitle>
          <CardDescription>Últimos produtos encontrados pelo monitor</CardDescription>
        </div>
        <Button
          variant="outline"
          size="sm"
          nativeButton={false}
          render={<Link href="/admin/produtos" />}
        >
          Ver todos
          <ArrowRight data-icon="inline-end" />
        </Button>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Produto</TableHead>
              <TableHead className="hidden md:table-cell">Preço</TableHead>
              <TableHead className="hidden lg:table-cell">Desconto</TableHead>
              <TableHead>Score</TableHead>
              <TableHead className="text-right">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {recent.map((product) => {
              const status = statusVariant[product.status]
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
                        <span className="max-w-52 truncate text-sm font-medium lg:max-w-72">
                          {product.title}
                        </span>
                        <span className="text-xs text-muted-foreground">{product.store}</span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">
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
                  <TableCell>
                    <ScoreBadge score={product.score} />
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge variant="secondary" className={status.className}>
                      {status.label}
                    </Badge>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
