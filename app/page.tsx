import { SiteHeader } from '@/components/landing/site-header'
import { SiteFooter } from '@/components/landing/site-footer'
import { Hero } from '@/components/landing/hero'
import { HowItWorks, Features } from '@/components/landing/features'
import { CTA } from '@/components/landing/cta'

export default function HomePage() {
  return (
    <div className="flex min-h-svh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <Hero />
        <HowItWorks />
        <Features />
        <CTA />
      </main>
      <SiteFooter />
    </div>
  )
}
