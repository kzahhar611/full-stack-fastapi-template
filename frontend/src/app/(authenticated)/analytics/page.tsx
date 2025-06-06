"use client"

import { useState } from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from "recharts"
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  FileText, 
  Users, 
  Clock,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select"

// Mock data for analytics
const monthlyData = [
  { month: 'Jan', rfps: 12, proposals: 8, won: 5, revenue: 850000 },
  { month: 'Feb', rfps: 15, proposals: 12, won: 7, revenue: 1200000 },
  { month: 'Mar', rfps: 18, proposals: 14, won: 9, revenue: 1650000 },
  { month: 'Apr', rfps: 22, proposals: 18, won: 12, revenue: 2100000 },
  { month: 'May', rfps: 25, proposals: 20, won: 14, revenue: 2400000 },
  { month: 'Jun', rfps: 28, proposals: 24, won: 16, revenue: 2850000 }
]

const performanceData = [
  { name: 'IT Services', value: 35, color: '#3b82f6' },
  { name: 'Consulting', value: 25, color: '#8b5cf6' },
  { name: 'Software Dev', value: 20, color: '#10b981' },
  { name: 'Marketing', value: 12, color: '#f59e0b' },
  { name: 'Others', value: 8, color: '#ef4444' }
]

const aiPerformanceData = [
  { metric: 'Analysis Speed', current: 85, target: 90 },
  { metric: 'Accuracy Rate', current: 94, target: 95 },
  { metric: 'Compliance Check', current: 98, target: 99 },
  { metric: 'Cost Estimation', current: 88, target: 92 },
  { metric: 'Risk Assessment', current: 91, target: 94 }
]

const weeklyActivity = [
  { day: 'Mon', rfps: 4, proposals: 3, reviews: 2 },
  { day: 'Tue', rfps: 6, proposals: 4, reviews: 3 },
  { day: 'Wed', rfps: 8, proposals: 6, reviews: 4 },
  { day: 'Thu', rfps: 5, proposals: 5, reviews: 3 },
  { day: 'Fri', rfps: 7, proposals: 5, reviews: 6 },
  { day: 'Sat', rfps: 2, proposals: 1, reviews: 1 },
  { day: 'Sun', rfps: 1, proposals: 1, reviews: 0 }
]

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("6months")
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive insights into your RFP performance and AI agent effectiveness
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7days">7 Days</SelectItem>
              <SelectItem value="30days">30 Days</SelectItem>
              <SelectItem value="3months">3 Months</SelectItem>
              <SelectItem value="6months">6 Months</SelectItem>
              <SelectItem value="1year">1 Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$2.85M</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
              +12.5% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">68.5%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
              +2.1% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active RFPs</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
              +3 new this week
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4.2 days</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingDown className="mr-1 h-3 w-3 text-red-500" />
              -0.8 days improved
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Revenue Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trend</CardTitle>
            <CardDescription>
              Monthly revenue from won RFPs over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `$${(value/1000000).toFixed(1)}M`} />
                <Tooltip formatter={(value) => [`$${(value as number).toLocaleString()}`, 'Revenue']} />
                <Area 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#3b82f6" 
                  fill="url(#colorRevenue)" 
                />
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* RFP Performance */}
        <Card>
          <CardHeader>
            <CardTitle>RFP Performance</CardTitle>
            <CardDescription>
              Monthly breakdown of RFPs, proposals, and wins
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="rfps" name="RFPs" fill="#8b5cf6" />
                <Bar dataKey="proposals" name="Proposals" fill="#10b981" />
                <Bar dataKey="won" name="Won" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Industry Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Industry Distribution</CardTitle>
            <CardDescription>
              RFP distribution across different industries
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={performanceData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {performanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Weekly Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Activity</CardTitle>
            <CardDescription>
              Daily breakdown of RFP activities this week
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weeklyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="rfps" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="RFPs"
                />
                <Line 
                  type="monotone" 
                  dataKey="proposals" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  name="Proposals"
                />
                <Line 
                  type="monotone" 
                  dataKey="reviews" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  name="Reviews"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* AI Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>AI Agent Performance</CardTitle>
          <CardDescription>
            Performance metrics for AI agents compared to targets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {aiPerformanceData.map((metric, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">{metric.metric}</p>
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">{metric.current}%</Badge>
                    <span className="text-xs text-muted-foreground">
                      Target: {metric.target}%
                    </span>
                  </div>
                </div>
                <div className="w-48">
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(metric.current / metric.target) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest RFP activities and system events
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                action: "RFP Analysis Completed",
                subject: "Enterprise Software Platform RFP",
                time: "2 minutes ago",
                status: "success"
              },
              {
                action: "Proposal Generated",
                subject: "Digital Marketing Campaign",
                time: "15 minutes ago", 
                status: "success"
              },
              {
                action: "Compliance Check Failed",
                subject: "Healthcare IT Infrastructure",
                time: "1 hour ago",
                status: "error"
              },
              {
                action: "New RFP Received",
                subject: "Cloud Migration Project",
                time: "2 hours ago",
                status: "info"
              },
              {
                action: "Proposal Submitted",
                subject: "Mobile App Development",
                time: "4 hours ago",
                status: "success"
              }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="space-y-1">
                  <p className="text-sm font-medium">{activity.action}</p>
                  <p className="text-xs text-muted-foreground">{activity.subject}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant={
                      activity.status === 'success' ? 'default' :
                      activity.status === 'error' ? 'destructive' : 'secondary'
                    }
                  >
                    {activity.status}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}