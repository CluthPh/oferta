'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  CheckCheck,
  Package,
  Tags,
  Settings,
  Zap,
  ExternalLink,
} from 'lucide-react'

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const navMain = [
  { title: 'Visão geral', url: '/admin', icon: LayoutDashboard },
  { title: 'Fila de aprovação', url: '/admin/aprovacao', icon: CheckCheck, badge: '3' },
  { title: 'Produtos', url: '/admin/produtos', icon: Package },
  { title: 'Nichos', url: '/admin/nichos', icon: Tags },
  { title: 'Configurações', url: '/admin/configuracoes', icon: Settings },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2.5 px-2 py-2">
          <div className="flex size-8 items-center justify-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
            <Zap className="size-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold leading-tight">OfertaBot</span>
            <span className="text-xs text-sidebar-foreground/60 leading-tight">
              Painel de controle
            </span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Gerenciamento</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navMain.map((item) => (
                <SidebarMenuItem key={item.url}>
                  <SidebarMenuButton
                    isActive={pathname === item.url}
                    render={<Link href={item.url} />}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                  {item.badge ? <SidebarMenuBadge>{item.badge}</SidebarMenuBadge> : null}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Canais</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton render={<a href="/ofertas" target="_blank" rel="noreferrer" />}>
                  <ExternalLink />
                  <span>Vitrine pública</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center gap-2 rounded-md bg-sidebar-accent px-3 py-2.5">
          <span className="relative flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-sidebar-primary opacity-75" />
            <span className="relative inline-flex size-2 rounded-full bg-sidebar-primary" />
          </span>
          <div className="flex flex-col">
            <span className="text-xs font-medium">Worker ativo</span>
            <span className="text-xs text-sidebar-foreground/60">Último ciclo: há 4 min</span>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
