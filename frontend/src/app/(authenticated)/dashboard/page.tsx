"use client"

import { useEffect, useState } from "react"
import { 
  FileText, 
  Bot, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  DollarSign,
  Users,
  Calendar,
  BarChart3,
  Building2,
  ChevronRight,
  Zap
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { SkeletonStats, SkeletonCard } from "@/components/ui/skeleton"
import { useAuthStore } from "@/stores/auth"
import { analyticsApi, rfpApi } from "@/lib/api"

// Mock data for demo
const dashboardStats = {
  totalRfps: 156,
  activeRfps: 24,
  completedRfps: 132,
  totalValue: 2850000,
  winRate: 68,
  avgResponseTime: 4.2,
}

const recentRfps = [
  {
    id: "1",
    title: "Enterprise Software Development",
    client: "TechCorp Inc.",
    deadline: "2024-01-15",
    value: 250000,
    status: "in_progress",
    priority: "high"
  },
  {
    id: "2", 
    title: "Digital Marketing Campaign",
    client: "Marketing Solutions Ltd.",
    deadline: "2024-01-20",
    value: 75000,
    status: "submitted",
    priority: "medium"
  },
  {
    id: "3",
    title: "Cloud Infrastructure Upgrade", 
    client: "CloudTech Systems",
    deadline: "2024-01-25",
    value: 180000,
    status: "draft",
    priority: "high"
  }
]

const quickActions = [
  {
    title: "Create New RFP",
    description: "Start a new RFP analysis",
    icon: FileText,
    href: "/rfps/new",
    color: "bg-blue-500"
  },
  {
    title: "Run AI Analysis",
    description: "Analyze existing RFPs",
    icon: Bot,
    href: "/ai/analyze",
    color: "bg-purple-500"
  },
  {
    title: "View Analytics",
    description: "Check performance metrics",
    icon: BarChart3,
    href: "/analytics",
    color: "bg-green-500"
  },
  {
    title: "Create Workflow",
    description: "Build AI workflow",
    icon: Clock,
    href: "/workflows/new",
    color: "bg-orange-500"
  }
]

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => setIsLoading(false), 1000)
  }, [])

  const getStatusBadge = (status: string) => {
    const variants = {
      in_progress: { variant: "default" as const, text: "In Progress" },
      submitted: { variant: "secondary" as const, text: "Submitted" },
      draft: { variant: "outline" as const, text: "Draft" },
      won: { variant: "default" as const, text: "Won" },
      lost: { variant: "destructive" as const, text: "Lost" }
    }
    
    const config = variants[status as keyof typeof variants] || variants.draft
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getPriorityColor = (priority: string) => {
    const colors = {
      high: "text-red-500",
      medium: "text-yellow-500", 
      low: "text-green-500"
    }
    return colors[priority as keyof typeof colors] || colors.medium
  }

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="h-8 w-64 shimmer rounded-lg"></div>
            <div className="h-5 w-80 shimmer rounded"></div>
          </div>
          <div className="h-10 w-40 shimmer rounded-lg"></div>
        </div>
        <SkeletonStats />
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <SkeletonCard />
          </div>
          <SkeletonCard />
        </div>
        <SkeletonCard />
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Welcome back, {user?.full_name?.split(" ")[0] || "User"}!
          </h1>
          <p className="text-muted-foreground text-lg">
            Here's what's happening with your RFPs today.
          </p>
        </div>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <FileText className="w-4 h-4 mr-2" />
          Create New RFP
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 hover:shadow-xl transition-all duration-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total RFPs</CardTitle>
            <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <FileText className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{dashboardStats.totalRfps}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400 flex items-center mt-1">
              <TrendingUp className="w-3 h-3 mr-1" />
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900 hover:shadow-xl transition-all duration-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 dark:text-orange-300">Active RFPs</CardTitle>
            <div className="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
              <Clock className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">{dashboardStats.activeRfps}</div>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              {dashboardStats.activeRfps} in progress
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 hover:shadow-xl transition-all duration-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Total Value</CardTitle>
            <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
              <DollarSign className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">
              ${(dashboardStats.totalValue / 1000000).toFixed(1)}M
            </div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              SAR {(dashboardStats.totalValue * 3.75 / 1000000).toFixed(1)}M equivalent
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 hover:shadow-xl transition-all duration-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Win Rate</CardTitle>
            <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
              <TrendingUp className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">{dashboardStats.winRate}%</div>
            <p className="text-xs text-purple-600 dark:text-purple-400 flex items-center mt-1">
              <TrendingUp className="w-3 h-3 mr-1" />
              +2.1% from last quarter
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent RFPs */}
        <Card className="lg:col-span-2 border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Recent RFPs
            </CardTitle>
            <CardDescription>
              Your most recent RFP submissions and their status
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y">
              {recentRfps.map((rfp, index) => (
                <div key={rfp.id} className="flex items-center justify-between p-6 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-gray-900 dark:text-white">{rfp.title}</h4>
                      <AlertCircle className={`h-4 w-4 ${getPriorityColor(rfp.priority)}`} />
                    </div>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <Building2 className="w-4 h-4" />
                      {rfp.client}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        Due: {new Date(rfp.deadline).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        ${rfp.value.toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="text-right space-y-3">
                    {getStatusBadge(rfp.status)}
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm">
                        View Details
                      </Button>
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950 dark:to-purple-950 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 p-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon
              return (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full justify-start h-auto p-4 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-all duration-200 group"
                  asChild
                >
                  <a href={action.href}>
                    <div className={`h-10 w-10 rounded-lg ${action.color} flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-200`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="text-left flex-1">
                      <div className="font-semibold text-gray-900 dark:text-white">{action.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {action.description}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                  </a>
                </Button>
              )
            })}
          </CardContent>
        </Card>
      </div>

      {/* Performance Overview */}
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950 dark:to-teal-950 rounded-t-lg">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Performance Overview
          </CardTitle>
          <CardDescription>
            Key metrics and trends for this quarter
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid gap-8 md:grid-cols-3">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-500" />
                  Response Time
                </span>
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  {dashboardStats.avgResponseTime} days avg
                </span>
              </div>
              <Progress value={75} className="h-3" />
              <p className="text-xs text-muted-foreground">
                Target: 3 days or less
              </p>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Completion Rate
                </span>
                <span className="text-sm font-medium text-green-600 dark:text-green-400">85%</span>
              </div>
              <Progress value={85} className="h-3" />
              <p className="text-xs text-muted-foreground">
                +5% from last month
              </p>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold flex items-center gap-2">
                  <Users className="w-4 h-4 text-purple-500" />
                  Client Satisfaction
                </span>
                <span className="text-sm font-medium text-purple-600 dark:text-purple-400">4.8/5</span>
              </div>
              <Progress value={96} className="h-3" />
              <p className="text-xs text-muted-foreground">
                Excellent rating
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}