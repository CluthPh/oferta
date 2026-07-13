'use client'

import * as React from 'react'
import { toast } from 'sonner'
import { Save } from 'lucide-react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from '@/components/ui/field'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const intervalItems = [
  { value: '5', label: 'A cada 5 minutos' },
  { value: '15', label: 'A cada 15 minutos' },
  { value: '30', label: 'A cada 30 minutos' },
  { value: '60', label: 'A cada 1 hora' },
]

export function SettingsForm() {
  const [dryRun, setDryRun] = React.useState(false)
  const [requireApproval, setRequireApproval] = React.useState(true)

  function handleSave(e: React.FormEvent) {
    e.preventDefault()
    toast.success('Configurações salvas', {
      description: 'As alterações serão aplicadas no próximo ciclo do worker.',
    })
  }

  return (
    <form onSubmit={handleSave} className="flex flex-col gap-4 md:gap-6">
      <div className="grid grid-cols-1 gap-4 md:gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Publicação</CardTitle>
            <CardDescription>Controle como as ofertas são publicadas no Telegram</CardDescription>
          </CardHeader>
          <CardContent>
            <FieldGroup>
              <Field orientation="horizontal">
                <div className="flex flex-col gap-0.5">
                  <FieldLabel htmlFor="dry-run">Modo simulação (DRY_RUN)</FieldLabel>
                  <FieldDescription>
                    Gera prévias sem publicar de verdade no canal
                  </FieldDescription>
                </div>
                <Switch id="dry-run" checked={dryRun} onCheckedChange={setDryRun} />
              </Field>
              <Field orientation="horizontal">
                <div className="flex flex-col gap-0.5">
                  <FieldLabel htmlFor="require-approval">Aprovação manual</FieldLabel>
                  <FieldDescription>
                    Ofertas entram na fila de aprovação antes de publicar
                  </FieldDescription>
                </div>
                <Switch
                  id="require-approval"
                  checked={requireApproval}
                  onCheckedChange={setRequireApproval}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="channel">Canal do Telegram</FieldLabel>
                <Input id="channel" defaultValue="@ofertasbr" />
                <FieldDescription>Canal onde as ofertas aprovadas são publicadas</FieldDescription>
              </Field>
            </FieldGroup>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monitoramento</CardTitle>
            <CardDescription>Parâmetros do ciclo de busca de ofertas</CardDescription>
          </CardHeader>
          <CardContent>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="interval">Intervalo entre ciclos</FieldLabel>
                <Select items={intervalItems} defaultValue="15">
                  <SelectTrigger id="interval">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      {intervalItems.map((item) => (
                        <SelectItem key={item.value} value={item.value}>
                          {item.label}
                        </SelectItem>
                      ))}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="min-score">Score mínimo global</FieldLabel>
                <Input id="min-score" type="number" defaultValue={70} min={0} max={100} />
                <FieldDescription>
                  Ofertas abaixo deste score são descartadas automaticamente
                </FieldDescription>
              </Field>
              <Field>
                <FieldLabel htmlFor="min-discount">Desconto mínimo (%)</FieldLabel>
                <Input id="min-discount" type="number" defaultValue={25} min={0} max={100} />
              </Field>
            </FieldGroup>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Afiliados</CardTitle>
          <CardDescription>Configuração dos links de afiliado do Mercado Livre</CardDescription>
        </CardHeader>
        <CardContent>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="affiliate-tag">Tag de afiliado</FieldLabel>
              <Input id="affiliate-tag" defaultValue="ofertabot-20" />
              <FieldDescription>
                Identificador aplicado automaticamente aos links publicados
              </FieldDescription>
            </Field>
          </FieldGroup>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button type="submit">
          <Save data-icon="inline-start" />
          Salvar alterações
        </Button>
      </div>
    </form>
  )
}
