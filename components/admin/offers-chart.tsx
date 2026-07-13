'use client'

import { Bar, BarChart, CartesianGrid, XAxis } from 'recharts'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { publishedPerDay } from '@/lib/demo-data'

const chartConfig = {
  encontradas: {
    label: 'Encontradas',
    color: 'var(--chart-5)',
  },
  publicadas: {
    label: 'Publicadas',
    color: 'var(--chart-1)',
  },
} satisfies ChartConfig

export function OffersChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ofertas nos últimos 7 dias</CardTitle>
        <CardDescription>Comparativo entre ofertas encontradas e publicadas</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-64 w-full">
          <BarChart accessibilityLayer data={publishedPerDay}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="date" tickLine={false} tickMargin={8} axisLine={false} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="encontradas" fill="var(--color-encontradas)" radius={4} />
            <Bar dataKey="publicadas" fill="var(--color-publicadas)" radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
