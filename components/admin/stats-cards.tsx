import { TrendingUp, Send, Gauge, MousePointerClick } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { stats } from '@/lib/demo-data'

const items = [
  {
    label: 'Ofertas encontradas hoje',
    value: String(stats.ofertasHoje),
    delta: stats.ofertasHojeDelta,
    icon: TrendingUp,
  },
  {
    label: 'Publicadas no Telegram',
    value: String(stats.publicadasHoje),
    delta: stats.publicadasHojeDelta,
    icon: Send,
  },
  {
    label: 'Score médio das ofertas',
    value: String(stats.scoreMedio),
    delta: stats.scoreMedioDelta,
    icon: Gauge,
  },
  {
    label: 'Cliques em links (7 dias)',
    value: stats.cliquesAfiliado.toLocaleString('pt-BR'),
    delta: stats.cliquesAfiliadoDelta,
    icon: MousePointerClick,
  },
]

export function StatsCards() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <Card key={item.label}>
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {item.label}
            </CardTitle>
            <item.icon className="size-4 text-muted-foreground" aria-hidden="true" />
          </CardHeader>
          <CardContent className="flex items-baseline gap-2">
            <span className="text-2xl font-semibold tabular-nums">{item.value}</span>
            <Badge variant="secondary" className="text-success">
              {item.delta}
            </Badge>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
