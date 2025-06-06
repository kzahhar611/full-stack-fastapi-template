"use client"

import { useState } from "react"
import { 
  Plus, 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  Clock,
  MapPin,
  Users,
  Filter,
  Search
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Mock data for calendar events
const events = [
  {
    id: "1",
    title: "RFP Deadline: IT Infrastructure",
    type: "deadline",
    date: "2025-01-05",
    time: "17:00",
    organization: "TechCorp Solutions",
    priority: "high"
  },
  {
    id: "2",
    title: "Proposal Presentation",
    type: "meeting",
    date: "2025-01-08",
    time: "14:00",
    organization: "Global Manufacturing",
    priority: "medium"
  },
  {
    id: "3",
    title: "Client Review Meeting",
    type: "meeting",
    date: "2025-01-10",
    time: "10:00",
    organization: "Healthcare Systems",
    priority: "high"
  },
  {
    id: "4",
    title: "RFP Submission Due",
    type: "deadline",
    date: "2025-01-12",
    time: "23:59",
    organization: "Strategic Consulting",
    priority: "critical"
  }
]

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date())

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startDayOfWeek = firstDay.getDay()

    const days = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push(null)
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day)
    }
    
    return days
  }

  const getEventsForDay = (day: number) => {
    if (!day) return []
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    return events.filter(event => event.date === dateStr)
  }

  const getPriorityColor = (priority: string) => {
    const colors = {
      critical: "bg-red-100 text-red-800",
      high: "bg-orange-100 text-orange-800",
      medium: "bg-yellow-100 text-yellow-800",
      low: "bg-green-100 text-green-800"
    }
    return colors[priority as keyof typeof colors] || colors.medium
  }

  const getTypeIcon = (type: string) => {
    return type === 'deadline' ? Clock : Users
  }

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ]

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  const navigateMonth = (direction: number) => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + direction, 1))
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Calendar
          </h1>
          <p className="text-muted-foreground text-lg">
            Track RFP deadlines, meetings, and important events
          </p>
        </div>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Event
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950 dark:to-red-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-red-700 dark:text-red-300">Critical Deadlines</CardTitle>
            <div className="p-2 bg-red-100 dark:bg-red-800 rounded-lg">
              <Clock className="h-4 w-4 text-red-600 dark:text-red-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-900 dark:text-red-100">
              {events.filter(e => e.priority === 'critical').length}
            </div>
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">
              This month
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Meetings</CardTitle>
            <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <Users className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
              {events.filter(e => e.type === 'meeting').length}
            </div>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              Scheduled this month
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 dark:text-orange-300">Deadlines</CardTitle>
            <div className="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
              <CalendarIcon className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
              {events.filter(e => e.type === 'deadline').length}
            </div>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              RFP deadlines
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Completed</CardTitle>
            <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
              <Clock className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">12</div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              Events completed
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Calendar */}
        <Card className="lg:col-span-2 border-0 shadow-lg">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <CalendarIcon className="w-5 h-5" />
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="icon"
                  onClick={() => navigateMonth(-1)}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  size="icon"
                  onClick={() => navigateMonth(1)}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 gap-1 mb-4">
              {dayNames.map(day => (
                <div key={day} className="p-2 text-center text-sm font-medium text-muted-foreground">
                  {day}
                </div>
              ))}
            </div>
            
            <div className="grid grid-cols-7 gap-1">
              {getDaysInMonth(currentDate).map((day, index) => {
                const dayEvents = getEventsForDay(day || 0)
                return (
                  <div 
                    key={index} 
                    className={`
                      min-h-[80px] p-1 border rounded-lg
                      ${day ? 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700' : 'bg-gray-50 dark:bg-gray-900'}
                      ${day === new Date().getDate() && 
                        currentDate.getMonth() === new Date().getMonth() && 
                        currentDate.getFullYear() === new Date().getFullYear() 
                        ? 'ring-2 ring-blue-500' : ''}
                    `}
                  >
                    {day && (
                      <>
                        <div className="text-sm font-medium mb-1">{day}</div>
                        <div className="space-y-1">
                          {dayEvents.slice(0, 2).map(event => {
                            const Icon = getTypeIcon(event.type)
                            return (
                              <div 
                                key={event.id}
                                className="text-xs p-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 truncate"
                              >
                                <Icon className="w-3 h-3 inline mr-1" />
                                {event.title}
                              </div>
                            )
                          })}
                          {dayEvents.length > 2 && (
                            <div className="text-xs text-muted-foreground">
                              +{dayEvents.length - 2} more
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Upcoming Events */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Upcoming Events
            </CardTitle>
            <CardDescription>
              Your next important deadlines and meetings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {events.map(event => {
              const Icon = getTypeIcon(event.type)
              return (
                <div key={event.id} className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-sm">{event.title}</h4>
                    <Badge className={getPriorityColor(event.priority)}>
                      {event.priority}
                    </Badge>
                  </div>
                  
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <CalendarIcon className="w-3 h-3" />
                      {new Date(event.date).toLocaleDateString()}
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3 h-3" />
                      {event.time}
                    </div>
                    <div className="flex items-center gap-2">
                      <Icon className="w-3 h-3" />
                      {event.organization}
                    </div>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}