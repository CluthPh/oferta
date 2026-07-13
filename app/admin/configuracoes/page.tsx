import { PageHeader } from '@/components/admin/page-header'
import { SettingsForm } from '@/components/admin/settings-form'

export default function SettingsPage() {
  return (
    <main className="flex flex-1 flex-col">
      <PageHeader
        title="Configurações"
        description="Ajuste o comportamento do monitor e da publicação"
      />
      <div className="flex flex-1 flex-col gap-4 p-4 md:p-6">
        <SettingsForm />
      </div>
    </main>
  )
}
