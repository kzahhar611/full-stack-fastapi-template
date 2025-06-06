"use client"

import { useState } from "react"
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Download, 
  Eye, 
  Edit, 
  Trash2,
  Bot,
  FileText,
  Calendar,
  DollarSign
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Mock data for RFPs
const rfps = [
  {
    id: "1",
    title: "Enterprise Software Development Platform",
    client: "TechCorp International",
    deadline: "2024-02-15",
    value: 750000,
    currency: "USD",
    status: "active",
    priority: "high",
    assignee: { name: "Sarah Johnson", avatar: "" },
    createdAt: "2024-01-05",
    lastActivity: "2 hours ago",
    aiScore: 85,
    compliance: 92
  },
  {
    id: "2",
    title: "Digital Marketing & Brand Strategy",
    client: "Marketing Solutions Ltd.",
    deadline: "2024-02-20",
    value: 125000,
    currency: "USD", 
    status: "submitted",
    priority: "medium",
    assignee: { name: "Michael Chen", avatar: "" },
    createdAt: "2024-01-08",
    lastActivity: "1 day ago",
    aiScore: 78,
    compliance: 88
  },
  {
    id: "3",
    title: "Cloud Infrastructure Migration",
    client: "CloudTech Systems",
    deadline: "2024-02-25",
    value: 450000,
    currency: "USD",
    status: "draft",
    priority: "high",
    assignee: { name: "Emily Rodriguez", avatar: "" },
    createdAt: "2024-01-10",
    lastActivity: "3 hours ago",
    aiScore: 91,
    compliance: 95
  },
  {
    id: "4",
    title: "Mobile Application Development",
    client: "StartupTech Inc.",
    deadline: "2024-03-01",
    value: 280000,
    currency: "USD",
    status: "review",
    priority: "medium",
    assignee: { name: "David Kim", avatar: "" },
    createdAt: "2024-01-12",
    lastActivity: "5 hours ago",
    aiScore: 73,
    compliance: 82
  },
  {
    id: "5",
    title: "Data Analytics & AI Implementation",
    client: "DataDriven Corp",
    deadline: "2024-03-10",
    value: 620000,
    currency: "USD",
    status: "won",
    priority: "high",
    assignee: { name: "Lisa Zhang", avatar: "" },
    createdAt: "2024-01-15",
    lastActivity: "1 week ago",
    aiScore: 94,
    compliance: 98
  }
]

const statusColors = {
  active: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  submitted: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300",
  review: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
  won: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  lost: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
}

const priorityColors = {
  high: "text-red-600 dark:text-red-400",
  medium: "text-yellow-600 dark:text-yellow-400",
  low: "text-green-600 dark:text-green-400"
}

export default function RFPsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedStatus, setSelectedStatus] = useState("all")

  const filteredRfps = rfps.filter(rfp => {
    const matchesSearch = rfp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rfp.client.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = selectedStatus === "all" || rfp.status === selectedStatus
    return matchesSearch && matchesStatus
  })

  const getStatusBadge = (status: string) => {
    return (
      <Badge variant="secondary" className={statusColors[status as keyof typeof statusColors]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0
    }).format(amount)
  }

  const getAIScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600 dark:text-green-400"
    if (score >= 80) return "text-yellow-600 dark:text-yellow-400"
    return "text-red-600 dark:text-red-400"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">RFP Management</h1>
          <p className="text-muted-foreground">
            Manage your Request for Proposals with AI-powered insights
          </p>
        </div>
        <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
          <Plus className="mr-2 h-4 w-4" />
          Create New RFP
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total RFPs</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rfps.length}</div>
            <p className="text-xs text-muted-foreground">
              Active projects in pipeline
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${(rfps.reduce((sum, rfp) => sum + rfp.value, 0) / 1000000).toFixed(1)}M
            </div>
            <p className="text-xs text-muted-foreground">
              Combined RFP value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg AI Score</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(rfps.reduce((sum, rfp) => sum + rfp.aiScore, 0) / rfps.length)}%
            </div>
            <p className="text-xs text-muted-foreground">
              AI analysis confidence
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Due This Week</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              Upcoming deadlines
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>RFP List</CardTitle>
          <CardDescription>
            Manage and track all your Request for Proposals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between space-x-4 mb-6">
            <div className="flex items-center space-x-2 flex-1">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search RFPs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    <Filter className="mr-2 h-4 w-4" />
                    Filter
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setSelectedStatus("all")}>
                    All Status
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setSelectedStatus("active")}>
                    Active
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSelectedStatus("submitted")}>
                    Submitted
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSelectedStatus("draft")}>
                    Draft
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSelectedStatus("review")}>
                    Review
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>

          {/* RFP Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>RFP Details</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Deadline</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>AI Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[70px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRfps.map((rfp) => (
                  <TableRow key={rfp.id}>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="font-medium">{rfp.title}</div>
                        <div className="text-sm text-muted-foreground">
                          ID: {rfp.id} • Created {rfp.createdAt}
                        </div>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="font-medium">{rfp.client}</div>
                      <div className="text-sm text-muted-foreground">
                        Last activity: {rfp.lastActivity}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="font-medium">
                        {formatCurrency(rfp.value, rfp.currency)}
                      </div>
                      <div className={`text-sm ${priorityColors[rfp.priority as keyof typeof priorityColors]}`}>
                        {rfp.priority.charAt(0).toUpperCase() + rfp.priority.slice(1)} Priority
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="font-medium">{rfp.deadline}</div>
                      <div className="text-sm text-muted-foreground">
                        {Math.ceil((new Date(rfp.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days left
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={rfp.assignee.avatar} />
                          <AvatarFallback>
                            {rfp.assignee.name.split(" ").map(n => n[0]).join("")}
                          </AvatarFallback>
                        </Avatar>
                        <div className="text-sm font-medium">{rfp.assignee.name}</div>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className={`font-medium ${getAIScoreColor(rfp.aiScore)}`}>
                        {rfp.aiScore}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {rfp.compliance}% compliance
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {getStatusBadge(rfp.status)}
                    </TableCell>
                    
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit RFP
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Bot className="mr-2 h-4 w-4" />
                            AI Analysis
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}