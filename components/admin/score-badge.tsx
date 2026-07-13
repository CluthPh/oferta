import { cn } from '@/lib/utils'

export function ScoreBadge({ score, className }: { score: number; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums',
        score >= 85
          ? 'bg-success/15 text-success'
          : score >= 70
            ? 'bg-warning/25 text-warning-foreground'
            : 'bg-muted text-muted-foreground',
        className,
      )}
    >
      {score}
      <span className="font-normal opacity-70">/100</span>
    </span>
  )
}
