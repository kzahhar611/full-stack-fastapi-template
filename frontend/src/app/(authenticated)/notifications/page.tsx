"use client"

import { useState } from "react"
import { 
  Bell, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Clock, 
  Settings,
  Filter,
  Mail,
  Trash2,
  Archive
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

// Mock data for notifications
const notifications = [
  {
    id: "1",
    type: "success",
    title: "RFP Submitted Successfully",
    message: "Your RFP for 'IT Infrastructure Upgrade' has been submitted to TechCorp Solutions.",
    timestamp: "2 minutes ago",
    read: false,
    category: "rfp"
  },
  {
    id: "2",
    type: "warning",
    title: "Deadline Approaching",
    message: "The deadline for 'Software Development Services' RFP is in 2 days.",
    timestamp: "1 hour ago",
    read: false,
    category: "deadline"
  },
  {
    id: "3",
    type: "info",
    title: "New AI Analysis Available",
    message: "AI analysis for 'Marketing Campaign RFP' has been completed with a score of 92%.",
    timestamp: "3 hours ago",
    read: true,
    category: "ai"
  },
  {
    id: "4",
    type: "error",
    title: "Document Upload Failed",
    message: "Failed to upload technical specifications document. Please try again.",
    timestamp: "5 hours ago",
    read: false,
    category: "error"
  },
  {
    id: "5",
    type: "success",
    title: "Team Member Added",
    message: "Sarah Johnson has been added to the Healthcare Systems Alliance project team.",
    timestamp: "1 day ago",
    read: true,
    category: "team"
  },
  {
    id: "6",
    type: "info",
    title: "Weekly Report Available",
    message: "Your weekly performance report is ready for review.",
    timestamp: "2 days ago",
    read: true,
    category: "report"
  },
  {
    id: "7",
    type: "warning",
    title: "Review Required",
    message: "Client has requested revisions to the proposal for Global Manufacturing Inc.",
    timestamp: "3 days ago",
    read: false,
    category: "review"
  },
  {
    id: "8",
    type: "success",
    title: "Proposal Accepted",
    message: "Congratulations! Your proposal for Strategic Consulting Group has been accepted.",
    timestamp: "1 week ago",
    read: true,
    category: "proposal"
  }
]

export default function NotificationsPage() {
  const [selectedFilter, setSelectedFilter] = useState("all")
  const [selectedCategory, setSelectedCategory] = useState("all")

  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = selectedFilter === "all" || 
                         (selectedFilter === "unread" && !notification.read) ||
                         (selectedFilter === "read" && notification.read)
    const matchesCategory = selectedCategory === "all" || notification.category === selectedCategory
    return matchesFilter && matchesCategory
  })

  const getNotificationIcon = (type: string) => {
    const icons = {
      success: CheckCircle,
      warning: AlertCircle,
      error: AlertCircle,
      info: Info
    }
    return icons[type as keyof typeof icons] || Info
  }

  const getNotificationColor = (type: string) => {
    const colors = {
      success: "text-green-600",
      warning: "text-yellow-600",
      error: "text-red-600",
      info: "text-blue-600"
    }
    return colors[type as keyof typeof colors] || "text-blue-600"
  }

  const getNotificationBg = (type: string) => {
    const colors = {
      success: "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800",
      warning: "bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800",
      error: "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800",
      info: "bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800"
    }
    return colors[type as keyof typeof colors] || "bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800"
  }

  const getCategoryBadge = (category: string) => {
    const variants = {
      rfp: { color: "bg-blue-100 text-blue-800", text: "RFP" },
      deadline: { color: "bg-red-100 text-red-800", text: "Deadline" },
      ai: { color: "bg-purple-100 text-purple-800", text: "AI" },
      error: { color: "bg-red-100 text-red-800", text: "Error" },
      team: { color: "bg-green-100 text-green-800", text: "Team" },
      report: { color: "bg-orange-100 text-orange-800", text: "Report" },
      review: { color: "bg-yellow-100 text-yellow-800", text: "Review" },
      proposal: { color: "bg-green-100 text-green-800", text: "Proposal" }
    }
    
    const config = variants[category as keyof typeof variants] || variants.rfp
    return <Badge className={config.color}>{config.text}</Badge>
  }

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Notifications
          </h1>
          <p className="text-muted-foreground text-lg">
            Stay updated with your RFP activities and important alerts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Mail className="mr-2 h-4 w-4" />
            Mark All Read
          </Button>
          <Button variant="outline">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Notifications</CardTitle>
            <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <Bell className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{notifications.length}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              All time notifications
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 dark:text-orange-300">Unread</CardTitle>
            <div className="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
              <AlertCircle className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">{unreadCount}</div>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              Require attention
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Today</CardTitle>
            <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
              <Clock className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">
              {notifications.filter(n => n.timestamp.includes('minute') || n.timestamp.includes('hour')).length}
            </div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              Received today
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Critical</CardTitle>
            <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
              <AlertCircle className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
              {notifications.filter(n => n.type === 'error' || n.type === 'warning').length}
            </div>
            <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
              High priority alerts
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filter: {selectedFilter === 'all' ? 'All' : selectedFilter}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={() => setSelectedFilter("all")}>
              All Notifications
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedFilter("unread")}>
              Unread Only
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedFilter("read")}>
              Read Only
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Category: {selectedCategory === 'all' ? 'All' : selectedCategory}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={() => setSelectedCategory("all")}>
              All Categories
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedCategory("rfp")}>
              RFP Updates
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedCategory("deadline")}>
              Deadlines
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedCategory("ai")}>
              AI Analysis
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedCategory("team")}>
              Team Updates
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.map((notification) => {
          const Icon = getNotificationIcon(notification.type)
          return (
            <Card 
              key={notification.id} 
              className={`border-0 shadow-sm hover:shadow-md transition-all duration-200 ${getNotificationBg(notification.type)} ${!notification.read ? 'border-l-4' : ''}`}
            >
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg ${notification.read ? 'bg-gray-100 dark:bg-gray-800' : 'bg-white dark:bg-gray-900'}`}>
                    <Icon className={`h-5 w-5 ${getNotificationColor(notification.type)}`} />
                  </div>
                  
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <h4 className={`font-semibold ${!notification.read ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-300'}`}>
                          {notification.title}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {notification.message}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {getCategoryBadge(notification.category)}
                        {!notification.read && (
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                        <Clock className="w-3 h-3" />
                        <span>{notification.timestamp}</span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        {!notification.read && (
                          <Button variant="ghost" size="sm">
                            <Mail className="w-4 h-4" />
                          </Button>
                        )}
                        <Button variant="ghost" size="sm">
                          <Archive className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="text-red-500 hover:text-red-700">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredNotifications.length === 0 && (
        <Card className="border-dashed border-2">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Bell className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Notifications Found</h3>
            <p className="text-muted-foreground text-center mb-4 max-w-md">
              No notifications match your current filter criteria. 
              Try adjusting your filters or check back later.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}