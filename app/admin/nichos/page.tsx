import { PageHeader } from '@/components/admin/page-header'
import { NichesGrid } from '@/components/admin/niches-grid'

export default function NichesPage() {
  return (
    <main className="flex flex-1 flex-col">
      <PageHeader
        title="Nichos"
        description="Defina as categorias e palavras-chave monitoradas pelo robô"
      />
      <div className="flex flex-1 flex-col gap-4 p-4 md:p-6">
        <NichesGrid />
      </div>
    </main>
  )
}
