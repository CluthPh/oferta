import {
  Send,
  Search,
  CheckCircle2,
  XCircle,
  TrendingDown,
} from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { activity, type ActivityItem } from '@/lib/demo-data'
import { cn } from '@/lib/utils'

const typeConfig: Record<
  ActivityItem['type'],
  { icon: typeof Send; className: string }
> = {
  publicado: { icon: Send, className: 'bg-primary/10 text-primary' },
  encontrado: { icon: Search, className: 'bg-warning/20 text-warning-foreground' },
  aprovado: { icon: CheckCircle2, className: 'bg-success/15 text-success' },
  rejeitado: { icon: XCircle, className: 'bg-destructive/10 text-destructive' },
  queda: { icon: TrendingDown, className: 'bg-success/15 text-success' },
}

export function ActivityFeed() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Atividade recente</CardTitle>
        <CardDescription>Últimos eventos do robô de ofertas</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-4">
          {activity.map((item) => {
            const config = typeConfig[item.type]
            return (
              <li key={item.id} className="flex items-start gap-3">
                <span
                  className={cn(
                    'flex size-8 shrink-0 items-center justify-center rounded-full',
                    config.className,
                  )}
                >
                  <config.icon className="size-4" aria-hidden="true" />
                </span>
                <div className="flex flex-col gap-0.5">
                  <p className="text-sm leading-snug text-pretty">{item.message}</p>
                  <span className="text-xs text-muted-foreground">{item.time}</span>
                </div>
              </li>
            )
          })}
        </ul>
      </CardContent>
    </Card>
  )
}
