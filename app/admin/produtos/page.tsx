import { PageHeader } from '@/components/admin/page-header'
import { ProductsTable } from '@/components/admin/products-table'

export default function ProductsPage() {
  return (
    <main className="flex flex-1 flex-col">
      <PageHeader
        title="Produtos"
        description="Todos os produtos monitorados e o status de publicação"
      />
      <div className="flex flex-1 flex-col gap-4 p-4 md:p-6">
        <ProductsTable />
      </div>
    </main>
  )
}
