import { PageHeader } from '@/components/admin/page-header'
import { ApprovalQueue } from '@/components/admin/approval-queue'

export default function ApprovalPage() {
  return (
    <main className="flex flex-1 flex-col">
      <PageHeader
        title="Fila de aprovação"
        description="Revise as ofertas encontradas antes de publicar no Telegram"
      />
      <div className="flex flex-1 flex-col gap-4 p-4 md:p-6">
        <ApprovalQueue />
      </div>
    </main>
  )
}
