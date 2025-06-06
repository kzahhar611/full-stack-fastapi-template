"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, 
  FileText, 
  Bot, 
  Workflow, 
  BarChart3, 
  Users, 
  Settings, 
  Building2, 
  Calendar, 
  Mail,
  Database,
  ChevronLeft,
  ChevronRight,
  Zap,
  Target
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip"

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: null,
  },
  {
    name: "RFPs",
    href: "/rfps",
    icon: FileText,
    badge: null,
  },
  {
    name: "RFP Analysis",
    href: "/rfp-analysis",
    icon: Zap,
    badge: "Module 1",
  },
  {
    name: "Compliance Analysis",
    href: "/compliance-analysis",
    icon: Target,
    badge: "Module 2",
  },
  {
    name: "AI Agents",
    href: "/agents",
    icon: Bot,
    badge: "New",
  },
  {
    name: "Workflows",
    href: "/workflows",
    icon: Workflow,
    badge: null,
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    badge: null,
  },
  {
    name: "Organizations",
    href: "/organizations",
    icon: Building2,
    badge: null,
  },
  {
    name: "Users",
    href: "/users",
    icon: Users,
    badge: null,
  },
  {
    name: "Calendar",
    href: "/calendar",
    icon: Calendar,
    badge: null,
  },
  {
    name: "Templates",
    href: "/templates",
    icon: Database,
    badge: null,
  },
  {
    name: "Notifications",
    href: "/notifications",
    icon: Mail,
    badge: "3",
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
    badge: null,
  },
]

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <TooltipProvider>
      <div
        className={cn(
          "flex flex-col border-r bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-all duration-300 shadow-lg",
          isCollapsed ? "w-16" : "w-64",
          className
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center border-b bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 px-4">
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">TenderWise AI</span>
                <span className="text-xs text-muted-foreground">Enterprise Edition</span>
              </div>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-8 w-8 hover:bg-white/50 dark:hover:bg-gray-800/50",
              isCollapsed ? "mx-auto" : "ml-auto"
            )}
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 p-4">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/")

            const navItem = (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-200 group",
                  isActive
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg"
                    : "text-muted-foreground hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-950 dark:hover:to-purple-950 hover:text-foreground",
                  isCollapsed && "justify-center px-2"
                )}
              >
                <Icon className={cn(
                  "h-5 w-5 shrink-0 transition-transform duration-200",
                  isActive ? "text-white" : "group-hover:scale-110"
                )} />
                {!isCollapsed && (
                  <>
                    <span className="truncate">{item.name}</span>
                    {item.badge && (
                      <span className={cn(
                        "ml-auto rounded-full px-2 py-0.5 text-xs font-medium",
                        isActive 
                          ? "bg-white/20 text-white" 
                          : "bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300"
                      )}>
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </Link>
            )

            if (isCollapsed) {
              return (
                <Tooltip key={item.name} delayDuration={0}>
                  <TooltipTrigger asChild>
                    {navItem}
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    {item.name}
                    {item.badge && ` (${item.badge})`}
                  </TooltipContent>
                </Tooltip>
              )
            }

            return navItem
          })}
        </nav>

        {/* Footer */}
        {!isCollapsed && (
          <div className="border-t bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 p-4">
            <div className="text-xs text-muted-foreground space-y-1">
              <p className="font-medium">TenderWise AI v1.0.0</p>
              <p className="flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Enterprise Edition
              </p>
            </div>
          </div>
        )}
      </div>
    </TooltipProvider>
  )
}