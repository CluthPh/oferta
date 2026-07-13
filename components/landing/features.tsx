import {
  Bot,
  Gauge,
  LineChart,
  Link2,
  ShieldCheck,
  Send,
  Search,
  BadgeCheck,
  Timer,
} from 'lucide-react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const steps = [
  {
    icon: Search,
    title: '1. Descoberta',
    description:
      'O robô varre o Mercado Livre continuamente pesquisando produtos nos nichos que você configurou.',
  },
  {
    icon: Gauge,
    title: '2. Pontuação',
    description:
      'Cada oferta recebe um score de até 100 pontos considerando desconto, queda de preço, frete grátis e reputação da loja.',
  },
  {
    icon: Send,
    title: '3. Publicação',
    description:
      'As melhores ofertas ganham link de afiliado e são publicadas automaticamente no canal do Telegram.',
  },
]

const features = [
  {
    icon: Bot,
    title: 'Monitoramento automático',
    description: 'Ciclos contínuos de busca sem intervenção manual, 24 horas por dia.',
  },
  {
    icon: LineChart,
    title: 'Histórico de preços',
    description: 'Registro da evolução de preço de cada produto para detectar quedas reais.',
  },
  {
    icon: BadgeCheck,
    title: 'Score de qualidade',
    description: 'Filtro inteligente que descarta falsas promoções e infla-preços.',
  },
  {
    icon: Link2,
    title: 'Links de afiliado',
    description: 'Monetização automática com sua tag de afiliado em todos os links.',
  },
  {
    icon: ShieldCheck,
    title: 'Fila de aprovação',
    description: 'Modo opcional em que você revisa cada oferta antes de publicar.',
  },
  {
    icon: Timer,
    title: 'Modo simulação',
    description: 'DRY_RUN gera prévias sem publicar, ideal para testar configurações.',
  },
]

export function HowItWorks() {
  return (
    <section id="como-funciona" className="mx-auto w-full max-w-6xl px-4 py-16 md:px-6 md:py-24">
      <div className="mx-auto mb-12 flex max-w-2xl flex-col items-center gap-3 text-center">
        <h2 className="text-balance text-3xl font-bold tracking-tight md:text-4xl">
          Como o OfertaBot funciona
        </h2>
        <p className="text-pretty leading-relaxed text-muted-foreground">
          Da descoberta à publicação, todo o fluxo é automatizado em três etapas.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3 md:gap-6">
        {steps.map((step) => (
          <Card key={step.title}>
            <CardHeader>
              <div className="mb-2 flex size-11 items-center justify-center rounded-lg bg-primary/10">
                <step.icon className="size-5 text-primary" aria-hidden="true" />
              </div>
              <CardTitle>{step.title}</CardTitle>
              <CardDescription className="leading-relaxed">{step.description}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
    </section>
  )
}

export function Features() {
  return (
    <section id="recursos" className="bg-card">
      <div className="mx-auto w-full max-w-6xl px-4 py-16 md:px-6 md:py-24">
        <div className="mx-auto mb-12 flex max-w-2xl flex-col items-center gap-3 text-center">
          <h2 className="text-balance text-3xl font-bold tracking-tight md:text-4xl">
            Tudo o que você precisa para um canal de ofertas
          </h2>
          <p className="text-pretty leading-relaxed text-muted-foreground">
            Recursos pensados para quem quer escalar um canal de ofertas com qualidade.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
          {features.map((feature) => (
            <Card key={feature.title} className="bg-background">
              <CardContent className="flex flex-col gap-3">
                <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="size-5 text-primary" aria-hidden="true" />
                </div>
                <h3 className="font-semibold">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
