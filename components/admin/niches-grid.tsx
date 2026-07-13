'use client'

import * as React from 'react'
import { toast } from 'sonner'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { niches as initialNiches, type Niche } from '@/lib/demo-data'

export function NichesGrid() {
  const [niches, setNiches] = React.useState<Niche[]>(initialNiches)

  function toggleNiche(id: string, active: boolean) {
    setNiches((prev) => prev.map((n) => (n.id === id ? { ...n, active } : n)))
    const niche = niches.find((n) => n.id === id)
    if (niche) {
      toast(active ? 'Nicho ativado' : 'Nicho pausado', {
        description: `${niche.name} ${active ? 'voltou a ser monitorado' : 'não será mais monitorado'}.`,
      })
    }
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {niches.map((niche) => (
        <Card key={niche.id} className={niche.active ? undefined : 'opacity-70'}>
          <CardHeader className="flex flex-row items-start justify-between gap-2">
            <div className="flex flex-col gap-1">
              <CardTitle className="text-base">{niche.name}</CardTitle>
              <CardDescription>
                {niche.productsFound} produtos encontrados · score mínimo {niche.minScore}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor={`niche-${niche.id}`} className="sr-only">
                Ativar nicho {niche.name}
              </Label>
              <Switch
                id={`niche-${niche.id}`}
                checked={niche.active}
                onCheckedChange={(checked) => toggleNiche(niche.id, checked)}
              />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1.5">
              {niche.keywords.map((keyword) => (
                <Badge key={keyword} variant="secondary">
                  {keyword}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
