import { PageHeader } from '@/components/admin/page-header'
import { StatsCards } from '@/components/admin/stats-cards'
import { OffersChart } from '@/components/admin/offers-chart'
import { ActivityFeed } from '@/components/admin/activity-feed'
import { RecentOffers } from '@/components/admin/recent-offers'
import { Badge } from '@/components/ui/badge'

export default function AdminDashboardPage() {
  return (
    <main className="flex flex-1 flex-col">
      <PageHeader
        title="Visão geral"
        description="Acompanhe o desempenho do monitor de ofertas em tempo real"
      >
        <Badge variant="secondary" className="hidden text-success sm:inline-flex">
          DRY_RUN desativado
        </Badge>
      </PageHeader>
      <div className="flex flex-1 flex-col gap-4 p-4 md:gap-6 md:p-6">
        <StatsCards />
        <div className="grid grid-cols-1 gap-4 md:gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <OffersChart />
          </div>
          <ActivityFeed />
        </div>
        <RecentOffers />
      </div>
    </main>
  )
}
