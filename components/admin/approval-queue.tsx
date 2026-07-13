'use client'

import * as React from 'react'
import Image from 'next/image'
import { toast } from 'sonner'
import {
  Check,
  X,
  Truck,
  BadgeCheck,
  LineChart as LineChartIcon,
  Inbox,
} from 'lucide-react'
import { Line, LineChart, CartesianGrid, XAxis, YAxis } from 'recharts'

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { ScoreBadge } from '@/components/admin/score-badge'
import {
  products,
  priceHistory,
  formatBRL,
  type Product,
} from '@/lib/demo-data'

const priceChartConfig = {
  price: {
    label: 'Preço',
    color: 'var(--chart-1)',
  },
} satisfies ChartConfig

function PriceHistoryDialog({ product }: { product: Product }) {
  const history = priceHistory[product.id]
  if (!history) return null

  return (
    <Dialog>
      <DialogTrigger render={<Button variant="ghost" size="sm" />}>
        <LineChartIcon data-icon="inline-start" />
        Histórico
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Histórico de preço</DialogTitle>
          <DialogDescription className="truncate">{product.title}</DialogDescription>
        </DialogHeader>
        <ChartContainer config={priceChartConfig} className="h-56 w-full">
          <LineChart accessibilityLayer data={history}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="date" tickLine={false} tickMargin={8} axisLine={false} />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `R$${v.toFixed(0)}`}
              width={52}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Line
              dataKey="price"
              type="monotone"
              stroke="var(--color-price)"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ChartContainer>
        <p className="text-sm text-muted-foreground">
          Menor preço registrado: <strong>{formatBRL(product.price)}</strong> — queda de{' '}
          {product.discount}% em relação ao preço de referência.
        </p>
      </DialogContent>
    </Dialog>
  )
}

export function ApprovalQueue() {
  const [queue, setQueue] = React.useState<Product[]>(
    products.filter((p) => p.status === 'pendente'),
  )

  function handleApprove(product: Product) {
    setQueue((prev) => prev.filter((p) => p.id !== product.id))
    toast.success('Oferta aprovada', {
      description: `${product.title} será publicada no Telegram.`,
    })
  }

  function handleReject(product: Product) {
    setQueue((prev) => prev.filter((p) => p.id !== product.id))
    toast('Oferta rejeitada', {
      description: `${product.title} foi removida da fila.`,
    })
  }

  if (queue.length === 0) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <Inbox />
          </EmptyMedia>
          <EmptyTitle>Fila vazia</EmptyTitle>
          <EmptyDescription>
            Nenhuma oferta aguardando aprovação. Novas ofertas aparecerão aqui assim que o
            monitor encontrá-las.
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {queue.map((product) => (
        <Card key={product.id} className="flex flex-col">
          <CardHeader className="flex flex-row items-start gap-4">
            <Image
              src={product.image || '/placeholder.svg'}
              alt={product.title}
              width={72}
              height={72}
              className="size-18 shrink-0 rounded-lg border bg-card object-cover"
            />
            <div className="flex min-w-0 flex-col gap-1.5">
              <CardTitle className="line-clamp-2 text-sm leading-snug text-pretty">
                {product.title}
              </CardTitle>
              <div className="flex flex-wrap items-center gap-1.5">
                <ScoreBadge score={product.score} />
                <Badge variant="secondary" className="text-success">
                  -{product.discount}%
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col gap-3">
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-semibold tabular-nums">
                {formatBRL(product.price)}
              </span>
              <span className="text-sm text-muted-foreground line-through tabular-nums">
                {formatBRL(product.oldPrice)}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-1.5">
              {product.officialStore ? (
                <Badge variant="outline">
                  <BadgeCheck data-icon="inline-start" />
                  Loja oficial
                </Badge>
              ) : null}
              {product.freeShipping ? (
                <Badge variant="outline">
                  <Truck data-icon="inline-start" />
                  Frete grátis
                </Badge>
              ) : null}
              <Badge variant="outline">{product.niche}</Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {product.store} · encontrada {product.foundAt}
            </p>
          </CardContent>
          <CardFooter className="flex items-center gap-2">
            <Button size="sm" className="flex-1" onClick={() => handleApprove(product)}>
              <Check data-icon="inline-start" />
              Aprovar
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="flex-1"
              onClick={() => handleReject(product)}
            >
              <X data-icon="inline-start" />
              Rejeitar
            </Button>
            <PriceHistoryDialog product={product} />
          </CardFooter>
        </Card>
      ))}
    </div>
  )
}
